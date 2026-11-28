"""Cœur de harness-mutant : copier le projet, injecter un défaut, lancer le harnais, compter.

Bibliothèque standard seulement. Repris du banc du talk (mesures/these-a/aveugle/injecter.py et
mesures/compter.py), rendu indépendant du projet : le harnais est une commande (code de sortie 0 =
vert), les défauts viennent d'un catalogue JSON extensible.
"""
from __future__ import annotations

import fnmatch
import json
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

IGNORES_COPIE = ("target", "build", ".git", "node_modules", ".gradle", ".idea", ".venv", "__pycache__")

# Qui a sonné ? Lu dans la sortie de la commande, dans cet ordre de priorité.
SIGNAUX = [
    ("ArchUnit", re.compile(r"Architecture Violation|Rule '.*?' was violated")),
    ("PMD", re.compile(r"PMD Failure|You have \d+ PMD violation|PMD violation", re.I)),
    ("CPD", re.compile(r"CPD Failure|You have \d+ CPD duplication", re.I)),
    ("SpotBugs", re.compile(r"BugInstance|Total bugs: [1-9]|SpotBugs", re.I)),
    ("Checkstyle", re.compile(r"checkstyle", re.I)),
    ("Error Prone", re.compile(r"\[\w+\] .*\(see https://errorprone\.info", re.I)),
    ("PIT", re.compile(r"Mutation score of \d+ is below threshold", re.I)),
    ("tests", re.compile(r"There are test failures|Tests run: \d+, Failures: [1-9]|Tests run: \d+, Failures: \d+, Errors: [1-9]|FAILED|AssertionError")),
]
# Champs du catalogue du banc (mesures/these-a/aveugle/defauts.json) qui ne servent pas à l'outil.
CHAMPS_DU_BANC = {"copie", "pourquoi_realiste"}
NE_COMPILE_PAS = re.compile(r"COMPILATION ERROR|cannot find symbol|error: incompatible types|SyntaxError")


@dataclass
class Defaut:
    id: str
    nom: str
    famille: str
    pourquoi: str = ""
    pour_l_attraper: str = ""
    regle_cousine: str | None = None
    fichiers: list[str] = field(default_factory=lambda: ["**/*.java"])
    chercher: str | None = None
    remplacer: str | None = None
    importer: list[str] = field(default_factory=list)
    remplacements: list[dict] = field(default_factory=list)  # forme exacte : fichier / avant / apres

    @classmethod
    def depuis(cls, d: dict) -> "Defaut":
        connus = set(cls.__dataclass_fields__)
        inconnus = set(d) - connus
        if inconnus:
            raise ValueError(f"{d.get('id', '?')} : champs inconnus {sorted(inconnus)}")
        defaut = cls(**d)
        if not defaut.remplacements and not (defaut.chercher and defaut.remplacer is not None):
            raise ValueError(f"{defaut.id} : il faut « chercher » + « remplacer », ou « remplacements »")
        if defaut.chercher:
            re.compile(defaut.chercher)
        return defaut


def charger_catalogue(chemins: list[str] | None) -> list[Defaut]:
    """Catalogues JSON {"defauts": [...]} ; sans chemin, le catalogue Java livré avec l'outil."""
    textes = []
    if not chemins:
        textes.append(resources.files("harness_mutant").joinpath("defauts/java.json").read_text("utf-8"))
    else:
        textes = [Path(c).read_text("utf-8") for c in chemins]
    defauts: list[Defaut] = []
    for t in textes:
        for d in json.loads(t)["defauts"]:
            defauts.append(Defaut.depuis({k: v for k, v in d.items() if k not in CHAMPS_DU_BANC}))
    ids = [d.id for d in defauts]
    doublons = {i for i in ids if ids.count(i) > 1}
    if doublons:
        raise ValueError(f"identifiants en double dans le catalogue : {sorted(doublons)}")
    return defauts


@dataclass
class Candidat:
    fichier: str
    ligne: int
    avant: str
    apres: str
    fichiers: dict[str, str]  # chemin relatif -> nouveau contenu


def _exclu(rel: str, exclusions: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, e) for e in exclusions)


def ajouter_imports(texte: str, imports: list[str]) -> str:
    """Ajoute les imports Java manquants juste après la déclaration de paquet."""
    manquants = [i for i in imports if not re.search(rf"^import\s+{re.escape(i)}\s*;", texte, re.M)]
    if not manquants:
        return texte
    lignes = "".join(f"import {i};\n" for i in manquants)
    m = re.search(r"^package\s+[\w.]+\s*;\s*\n", texte, re.M)
    if not m:
        return lignes + texte
    return texte[:m.end()] + "\n" + lignes + texte[m.end():]


def lignes_ajoutees(diff: str) -> dict[str, set[int]]:
    """Lignes ajoutées par un diff unifié (git diff), numérotées dans l'arbre APRÈS le changement."""
    res: dict[str, set[int]] = {}
    fichier, n = None, 0
    for l in diff.splitlines():
        if l.startswith("+++ "):
            chemin = l[4:].split("\t")[0].strip()
            fichier = None if chemin == "/dev/null" else (chemin[2:] if chemin.startswith("b/") else chemin)
        elif l.startswith("@@"):
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", l)
            n = int(m.group(1)) if m else 0
        elif fichier and l.startswith("+"):
            res.setdefault(fichier, set()).add(n)
            n += 1
        elif fichier and l.startswith(" "):
            n += 1
    return res


def diff_git(projet: Path, base: str) -> str:
    p = subprocess.run(["git", "diff", "-U0", base, "--", "."], cwd=projet, capture_output=True, text=True)
    if p.returncode != 0:
        raise ValueError(f"git diff {base} a échoué : {p.stderr.strip()}")
    return p.stdout


def candidats(racine: Path, d: Defaut, exclusions: list[str],
              cibles: dict[str, set[int]] | None = None) -> list[Candidat]:
    """Tous les endroits où le défaut s'applique, dans un ordre stable (fichier, puis position).

    cibles : si donné, seuls les endroits qui touchent une de ces lignes (ex. les lignes écrites par l'agent)."""
    res: list[Candidat] = []
    if d.remplacements:
        # Forme exacte (compatible avec defauts.json du banc) : un seul candidat, tous les remplacements.
        nouveaux: dict[str, str] = {}
        premier = None
        for r in d.remplacements:
            f = racine / r["fichier"]
            if r.get("nouveau_fichier"):
                if f.exists():
                    return []
                nouveaux[r["fichier"]] = r["apres"]
                premier = premier or (r["fichier"], 1, "", r["apres"])
                continue
            if not f.is_file():
                return []
            s = nouveaux.get(r["fichier"], f.read_text("utf-8"))
            if s.count(r["avant"]) != 1:
                return []
            if premier is None:
                premier = (r["fichier"], s[:s.index(r["avant"])].count("\n") + 1, r["avant"], r["apres"])
            nouveaux[r["fichier"]] = s.replace(r["avant"], r["apres"])
        fichier, ligne, avant, apres = premier
        if cibles is not None and not any(cibles.get(f) for f in nouveaux):
            return []
        res.append(Candidat(fichier, ligne, avant, apres, nouveaux))
        return res
    motif = re.compile(d.chercher, re.M)
    vus: set[Path] = set()
    for g in d.fichiers:
        for f in sorted(racine.glob(g)):
            if f in vus or not f.is_file():
                continue
            vus.add(f)
            rel = f.relative_to(racine).as_posix()
            if _exclu(rel, exclusions):
                continue
            s = f.read_text("utf-8", errors="replace")
            for m in motif.finditer(s):
                apres = m.expand(d.remplacer)
                if apres == m.group(0):
                    continue
                if cibles is not None:
                    debut = s[:m.start()].count("\n") + 1
                    fin = debut + m.group(0).count("\n")
                    if not cibles.get(rel, set()) & set(range(debut, fin + 1)):
                        continue
                nouveau = ajouter_imports(s[:m.start()] + apres + s[m.end():], d.importer)
                ligne = s[:m.start()].count("\n") + 1
                res.append(Candidat(rel, ligne, m.group(0), apres, {rel: nouveau}))
    return res


def appliquer(racine: Path, c: Candidat) -> dict[Path, str | None]:
    """Écrit le défaut ; renvoie le contenu d'origine des fichiers touchés (pour les remettre)."""
    origine: dict[Path, str | None] = {}
    for rel, texte in c.fichiers.items():
        f = racine / rel
        origine[f] = f.read_text("utf-8") if f.exists() else None
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(texte, "utf-8")
    return origine


def remettre(origine: dict[Path, str | None]) -> None:
    for f, texte in origine.items():
        if texte is None:
            f.unlink(missing_ok=True)
        else:
            f.write_text(texte, "utf-8")


@dataclass
class Execution:
    code: int
    duree: float
    sortie: str
    delai_depasse: bool = False


def lancer(commande: str, dossier: Path, delai: int) -> Execution:
    debut = time.monotonic()
    try:
        p = subprocess.run(commande, shell=True, cwd=dossier, capture_output=True, text=True, timeout=delai)
        return Execution(p.returncode, time.monotonic() - debut, (p.stdout or "") + (p.stderr or ""))
    except subprocess.TimeoutExpired as e:
        sortie = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        return Execution(-1, time.monotonic() - debut, sortie, delai_depasse=True)


def qui_a_sonne(sortie: str) -> list[str]:
    return [nom for nom, motif in SIGNAUX if motif.search(sortie)]


def copier_projet(projet: Path, cible: Path) -> Path:
    dest = cible / projet.resolve().name
    shutil.copytree(projet, dest, ignore=shutil.ignore_patterns(*IGNORES_COPIE), symlinks=True)
    return dest


@dataclass
class Resultat:
    defaut: Defaut
    statut: str  # attrape | trou | non_applicable | ne_compile_pas
    fichier: str | None = None
    ligne: int | None = None
    avant: str | None = None
    apres: str | None = None
    signaux: list[str] = field(default_factory=list)
    duree: float = 0.0

    def en_dict(self) -> dict:
        return {
            "id": self.defaut.id, "nom": self.defaut.nom, "famille": self.defaut.famille,
            "statut": self.statut, "fichier": self.fichier, "ligne": self.ligne,
            "avant": self.avant, "apres": self.apres, "signaux": self.signaux,
            "regle_cousine": self.defaut.regle_cousine, "pour_l_attraper": self.defaut.pour_l_attraper,
            "duree_s": round(self.duree, 1),
        }


def sonder(projet: Path, commande: str, defauts: list[Defaut], exclusions: list[str], delai: int = 900,
           essais: int = 3, journal=print, cibles: dict[str, set[int]] | None = None) -> dict:
    """Lance la sonde complète ; renvoie un dict prêt à afficher ou à écrire en JSON."""
    travail = Path(tempfile.mkdtemp(prefix="harness-mutant-"))
    try:
        copie = copier_projet(projet, travail)
        journal(f"Témoin : « {commande} » sur le projet sans défaut…")
        temoin = lancer(commande, copie, delai)
        if temoin.code != 0:
            return {"erreur": "le harnais est rouge AVANT toute injection : corrigez-le d'abord",
                    "code": temoin.code, "extrait": temoin.sortie[-3000:]}
        journal(f"Témoin vert en {temoin.duree:.0f} s. {len(defauts)} défauts au catalogue.")
        resultats: list[Resultat] = []
        for d in defauts:
            cands = candidats(copie, d, exclusions, cibles)
            if not cands:
                resultats.append(Resultat(d, "non_applicable"))
                journal(f"  {d.id} {d.nom} : non applicable (motif absent)")
                continue
            r = None
            for c in cands[:essais]:
                origine = appliquer(copie, c)
                try:
                    ex = lancer(commande, copie, delai)
                finally:
                    remettre(origine)
                if ex.code != 0 and not ex.delai_depasse and NE_COMPILE_PAS.search(ex.sortie):
                    r = Resultat(d, "ne_compile_pas", c.fichier, c.ligne, c.avant, c.apres, duree=ex.duree)
                    continue  # défaut non viable à cet endroit : on essaie le suivant
                if ex.delai_depasse:
                    r = Resultat(d, "attrape", c.fichier, c.ligne, c.avant, c.apres, ["délai dépassé"], ex.duree)
                elif ex.code != 0:
                    r = Resultat(d, "attrape", c.fichier, c.ligne, c.avant, c.apres,
                                 qui_a_sonne(ex.sortie) or [f"code de sortie {ex.code}"], ex.duree)
                else:
                    r = Resultat(d, "trou", c.fichier, c.ligne, c.avant, c.apres, duree=ex.duree)
                break
            resultats.append(r)
            journal(f"  {d.id} {d.nom} : {r.statut}" + (f" ({', '.join(r.signaux)})" if r.signaux else ""))
        return synthese(projet, commande, temoin.duree, resultats)
    finally:
        shutil.rmtree(travail, ignore_errors=True)


def synthese(projet: Path, commande: str, duree_temoin: float, resultats: list[Resultat]) -> dict:
    comptes = [r for r in resultats if r.statut in ("attrape", "trou")]
    attrapes = [r for r in comptes if r.statut == "attrape"]
    par_signal: dict[str, int] = {}
    for r in attrapes:
        for s in r.signaux[:1]:  # le premier signal, pour que la somme fasse le total
            par_signal[s] = par_signal.get(s, 0) + 1
    par_famille: dict[str, list[int]] = {}
    for r in comptes:
        a, n = par_famille.get(r.defaut.famille, [0, 0])
        par_famille[r.defaut.famille] = [a + (r.statut == "attrape"), n + 1]
    return {
        "projet": str(projet), "commande": commande, "duree_temoin_s": round(duree_temoin, 1),
        "comptes": len(comptes), "attrapes": len(attrapes),
        "score": round(100 * len(attrapes) / len(comptes)) if comptes else None,
        "par_signal": par_signal, "par_famille": par_famille,
        "non_applicables": [r.defaut.id for r in resultats if r.statut == "non_applicable"],
        "ne_compilent_pas": [r.defaut.id for r in resultats if r.statut == "ne_compile_pas"],
        "resultats": [r.en_dict() for r in resultats],
    }
