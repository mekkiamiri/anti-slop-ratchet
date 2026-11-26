"""Mesure du « harnais aveugle » : ce que l'agent a ajouté, vu par des outils déterministes.

Pour chaque copie gardée par lancer.py --garder (tags git « départ » = 1er commit, « agent » = code rendu) :
  1. exporte l'arbre « agent » dans un dossier jetable, sans les règles du talk ni les mauvais exemples
     (rules/, slopexamples/, .claude/, CLAUDE.md) : on mesure le code produit, pas le harnais ;
  2. ajoute au pom la configuration d'analyse (PMD 7.17.0 + CPD par maven-pmd-plugin 3.28.0,
     SpotBugs 4.10.5, JaCoCo 0.8.14), tout hors ligne (mvn -o) ;
  3. croise les rapports avec les lignes AJOUTÉES (git diff -U0 départ..agent) : seul le nouveau compte.

Sortie : une ligne JSON par copie (chemins relatifs au projet uniquement) + le diff de chaque copie.

Usage :
  python3 analyser.py --copies sonnet=<dossier> --copies opus=<dossier> --sortie mesures.jsonl --diffs diffs/
Heuristiques (documentées dans le README) : voir les constantes MOTIF_*.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tarfile
import io
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ICI = Path(__file__).resolve().parent
EXCLUS = ("src/test/java/io/github/mekkiamiri/ratchet/rules", "src/test/java/io/github/mekkiamiri/slopexamples",
          ".claude", "CLAUDE.md")
NOM_COPIE = re.compile(r"^(T\d\d)-([ABC])-(\d+)$")

PLUGINS = """            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-pmd-plugin</artifactId>
                <version>3.28.0</version>
                <configuration>
                    <rulesets><ruleset>@REGLES@</ruleset></rulesets>
                    <includeTests>true</includeTests>
                    <minimumTokens>50</minimumTokens>
                    <format>xml</format>
                    <linkXRef>false</linkXRef>
                </configuration>
            </plugin>
            <plugin>
                <groupId>com.github.spotbugs</groupId>
                <artifactId>spotbugs-maven-plugin</artifactId>
                <version>4.10.5.0</version>
                <configuration>
                    <includeTests>true</includeTests>
                    <effort>Max</effort>
                    <threshold>Low</threshold>
                </configuration>
            </plugin>
"""
GOALS = ["org.jacoco:jacoco-maven-plugin:0.8.14:prepare-agent", "test", "org.jacoco:jacoco-maven-plugin:0.8.14:report",
         "pmd:pmd", "pmd:cpd", "spotbugs:spotbugs", "-Dmaven.test.failure.ignore=true"]

# Assertion : appel à une méthode d'assertion JUnit/AssertJ/Mockito/MockMvc.
MOTIF_ASSERT = re.compile(r"\b(assert\w*|fail|verify|andExpect|expectThrows)\s*\(")
# Heuristique « cas limite » sur le nom ET le corps du test (insensible à la casse).
MOTIFS_CAS = {
    "null_vide": re.compile(r"null|empty|vide|blank|absent|missing|manquant|aucun|isEmpty|Optional\.empty|"
                            r"no_?orders|sans_?commande|zero_?lines?|\b0 commande", re.I),
    "erreur": re.compile(r"exception|throw|reject|refus|invalid|invalide|not_?found|introuvable|inexist|unknown|"
                         r"inconnu|isNotFound|isBadRequest|isConflict|status\(\)\.is4|40[0-9]|422|already|déjà|cannot|"
                         r"impossible|interdit", re.I),
    "frontiere": re.compile(r"exactly|exactement|boundary|limite|seuil|threshold|equal_?to|égal|just_?(above|below)|"
                            r"juste|at_?the|edge|negative|négati", re.I),
}
MOTIF_TEST = re.compile(r"@(Test|ParameterizedTest|RepeatedTest)\b")
MOTIF_METHODE = re.compile(
    r"^\s*(?:(?:public|protected|private|static|final|synchronized|abstract|default)\s+)*"
    r"(?:<[^>]+>\s+)?[\w<>\[\],.?]+(?:\s*<[^>]*>)?\s+(\w+)\s*\([^;{]*\)?\s*(?:throws\s+[\w., ]+)?\s*\{?\s*$")
MOTIF_TYPE = re.compile(r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|protected|private|static|final|abstract|sealed|"
                        r"non-sealed|strictfp)\s+)*(class|interface|record|enum|@interface)\s+(\w+)")
MOTS_CLES = {"if", "for", "while", "switch", "catch", "return", "new", "else", "try", "synchronized", "do", "throw"}
# Méthodes appelées par le framework (ou par contrat) : pas du code mort même sans appel dans le code.
ANNOT_FRAMEWORK = re.compile(r"@(Override|Bean|Scheduled|EventListener|ExceptionHandler|PostConstruct|PreDestroy|"
                             r"(Get|Post|Put|Delete|Patch|Request)Mapping|Test|ParameterizedTest|BeforeEach|AfterEach|"
                             r"BeforeAll|AfterAll|TransactionalEventListener|JsonProperty|JsonCreator|JsonValue)\b")
ANNOT_SPRING_TYPE = re.compile(r"@(Component|Service|Repository|RestController|Controller|Configuration|"
                               r"ControllerAdvice|RestControllerAdvice|SpringBootApplication|EnableScheduling)\b")


def sh(cmd: list[str], cwd: Path, env: dict | None = None, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


def exclu(rel: str) -> bool:
    return any(rel == e or rel.startswith(e + "/") for e in EXCLUS)


def exporter(copie: Path, ref: str, dest: Path) -> None:
    data = subprocess.run(["git", "archive", ref], cwd=copie, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(dest, filter="data")
    for e in EXCLUS:
        p = dest / e
        shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)


def lignes_ajoutees(copie: Path, depart: str) -> dict[str, set[int]]:
    """{chemin relatif: {numéros de lignes ajoutées dans l'arbre agent}} (fichiers hors harnais)."""
    diff = sh(["git", "diff", "-U0", "--no-color", "--no-renames", depart, "agent"], copie).stdout
    res: dict[str, set[int]] = {}
    courant = None
    for l in diff.splitlines():
        if l.startswith("+++ "):
            chemin = l[4:]
            courant = None if chemin == "/dev/null" else chemin[2:]
            if courant and exclu(courant):
                courant = None
            if courant:
                res.setdefault(courant, set())
        elif l.startswith("@@") and courant:
            m = re.search(r"\+(\d+)(?:,(\d+))?", l)
            debut, n = int(m.group(1)), int(m.group(2) or 1)
            res[courant].update(range(debut, debut + n))
    return {k: v for k, v in res.items() if v}


def fichiers_supprimes(copie: Path, depart: str) -> list[str]:
    out = sh(["git", "diff", "--name-status", "--no-renames", depart, "agent"], copie).stdout
    return [l.split("\t", 1)[1] for l in out.splitlines() if l.startswith("D\t") and not exclu(l.split("\t", 1)[1])]


def preparer_pom(arbre: Path, regles: Path) -> None:
    pom = arbre / "pom.xml"
    s = pom.read_text()
    s = s.replace("        </plugins>\n    </build>",
                  PLUGINS.replace("@REGLES@", str(regles)) + "        </plugins>\n    </build>", 1)
    pom.write_text(s)


def analyser_arbre(arbre: Path, env: dict) -> dict:
    preparer_pom(arbre, ICI / "regles-pmd.xml")
    p = sh(["mvn", "-o", "-q", "-B", *GOALS], arbre, env)
    t = arbre / "target"
    return {"rc": p.returncode, "compile": "COMPILATION ERROR" not in (p.stdout + p.stderr),
            "pmd": t / "pmd.xml", "cpd": t / "cpd.xml", "spotbugs": t / "spotbugsXml.xml",
            "jacoco": t / "site" / "jacoco" / "jacoco.xml", "surefire": t / "surefire-reports",
            "journal": (p.stdout + p.stderr)[-1500:]}


def rel_depuis(chemin: str, arbre: Path) -> str:
    try:
        return str(Path(chemin).resolve().relative_to(arbre.resolve()))
    except ValueError:
        return chemin


def lire_pmd(xml: Path, arbre: Path) -> list[dict]:
    if not xml.exists():
        return []
    ns = {"p": "http://pmd.sourceforge.net/report/2.0.0"}
    out = []
    for f in ET.parse(xml).getroot().findall("p:file", ns):
        rel = rel_depuis(f.get("name"), arbre)
        for v in f.findall("p:violation", ns):
            out.append({"fichier": rel, "ligne": int(v.get("beginline")), "fin": int(v.get("endline")),
                        "regle": v.get("rule"), "message": (v.text or "").strip()})
    return out


def complexite_totale(violations: list[dict]) -> dict[str, int]:
    """Somme des complexités de classe (règle CyclomaticComplexity, niveau 1) par zone main/test."""
    tot = {"main": 0, "test": 0}
    for v in violations:
        if v["regle"] != "CyclomaticComplexity":
            continue
        m = re.search(r"total cyclomatic complexity of (\d+)", v["message"])
        if m:
            tot["main" if v["fichier"].startswith("src/main") else "test"] += int(m.group(1))
    return tot


def complexites_methodes(violations: list[dict]) -> list[dict]:
    out = []
    for v in violations:
        m = re.search(r"(?:method|constructor) '([^']+)' has a cyclomatic complexity of (\d+)", v["message"])
        if v["regle"] == "CyclomaticComplexity" and m:
            out.append({"fichier": v["fichier"], "ligne": v["ligne"], "fin": v["fin"], "methode": m.group(1),
                        "cc": int(m.group(2))})
    return out


def touche(ajout: dict[str, set[int]], fichier: str, debut: int, fin: int) -> bool:
    lignes = ajout.get(fichier)
    return bool(lignes) and any(n in lignes for n in range(debut, fin + 1))


def lire_cpd(xml: Path, arbre: Path, ajout: dict[str, set[int]]) -> list[dict]:
    if not xml.exists():
        return []
    racine = ET.parse(xml).getroot()
    out = []
    for d in racine.iter():
        if not d.tag.endswith("duplication"):
            continue
        occ = [(rel_depuis(f.get("path"), arbre), int(f.get("line")), int(f.get("endline") or f.get("line")))
               for f in d if f.tag.endswith("file")]
        if any(touche(ajout, f, a, b) for f, a, b in occ):
            out.append({"lignes": int(d.get("lines")), "jetons": int(d.get("tokens")),
                        "occurrences": [f"{f}:{a}-{b}" for f, a, b in occ],
                        "avec_existant": not all(touche(ajout, f, a, b) for f, a, b in occ)})
    return out


def lire_spotbugs(xml: Path, ajout: dict[str, set[int]]) -> list[dict]:
    if not xml.exists():
        return []
    out = []
    for b in ET.parse(xml).getroot().iter("BugInstance"):
        sl = b.find("SourceLine")
        if sl is None:
            m = b.find("Method")
            sl = m.find("SourceLine") if m is not None else None
        if sl is None or not sl.get("sourcepath"):
            continue
        sp = sl.get("sourcepath")
        debut = int(sl.get("start") or 0)
        fin = int(sl.get("end") or debut)
        for zone in ("src/main/java/", "src/test/java/"):
            f = zone + sp
            if f in ajout and (touche(ajout, f, debut, fin) or debut == 0):
                out.append({"type": b.get("type"), "categorie": b.get("category"), "fichier": f, "ligne": debut})
    return out


def lire_jacoco(xml: Path, ajout: dict[str, set[int]]) -> dict:
    res = {"lignes_executables_ajoutees": 0, "lignes_couvertes_ajoutees": 0}
    if not xml.exists():
        return res | {"absent": True}
    racine = ET.parse(xml).getroot()
    for pkg in racine.iter("package"):
        for sf in pkg.iter("sourcefile"):
            f = f"src/main/java/{pkg.get('name')}/{sf.get('name')}"
            lignes = ajout.get(f)
            if not lignes:
                continue
            for l in sf.iter("line"):
                if int(l.get("nr")) in lignes:
                    res["lignes_executables_ajoutees"] += 1
                    res["lignes_couvertes_ajoutees"] += int(int(l.get("ci")) > 0)
    return res


def corps(lignes: list[str], i: int) -> tuple[int, str]:
    """Depuis la ligne i (déclaration), renvoie (ligne de fin, texte du corps entre accolades)."""
    prof, vu, texte = 0, False, []
    for j in range(i, len(lignes)):
        l = re.sub(r'"(?:\\.|[^"\\])*"', '""', lignes[j])
        texte.append(lignes[j])
        prof += l.count("{") - l.count("}")
        vu = vu or "{" in l
        if vu and prof <= 0:
            return j, "\n".join(texte)
    return len(lignes) - 1, "\n".join(texte)


def tests_ajoutes(arbre: Path, ajout: dict[str, set[int]]) -> list[dict]:
    out = []
    for f, lignes_aj in ajout.items():
        if not (f.startswith("src/test/") and f.endswith(".java")):
            continue
        src = (arbre / f).read_text().splitlines()
        aides = {}  # méthodes non-test de la classe qui contiennent une assertion (assertion indirecte)
        for i, l in enumerate(src):
            m = MOTIF_METHODE.match(l)
            if m and m.group(1) not in MOTS_CLES:
                _, c = corps(src, i)
                if MOTIF_ASSERT.search("\n".join(c.splitlines()[1:])):
                    aides[m.group(1)] = True
        for i, l in enumerate(src):
            if not MOTIF_TEST.search(l):
                continue
            j = i + 1
            while j < len(src) and not re.search(r"\w+\s*\(", src[j]) or (j < len(src) and src[j].strip().startswith("@")):
                j += 1
            if j >= len(src) or (j + 1) not in lignes_aj:
                continue
            m = re.search(r"(\w+)\s*\(", src[j])
            fin, c = corps(src, j)
            c_corps = "\n".join(c.splitlines()[1:])
            n_assert = len(MOTIF_ASSERT.findall(c_corps))
            indirect = any(re.search(rf"\b{re.escape(a)}\s*\(", c_corps) for a in aides)
            texte = (m.group(1) if m else "") + "\n" + c
            out.append({"fichier": f, "ligne": j + 1, "nom": m.group(1) if m else "?", "assertions": n_assert,
                        "assertion_indirecte": indirect,
                        **{k: bool(rx.search(texte)) for k, rx in MOTIFS_CAS.items()}})
    return out


def types_et_methodes(arbre: Path, ajout: dict[str, set[int]]) -> tuple[list[dict], list[dict]]:
    types, methodes = [], []
    for f, lignes_aj in ajout.items():
        if not f.endswith(".java"):
            continue
        src = (arbre / f).read_text().splitlines()
        for i, l in enumerate(src):
            if (i + 1) not in lignes_aj:
                continue
            avant = "\n".join(src[max(0, i - 4):i + 1])
            mt = MOTIF_TYPE.match(l)
            if mt:
                types.append({"fichier": f, "ligne": i + 1, "genre": mt.group(1), "nom": mt.group(2),
                              "zone": "main" if f.startswith("src/main") else "test",
                              "spring": bool(ANNOT_SPRING_TYPE.search(avant))})
                continue
            mm = MOTIF_METHODE.match(l)
            if mm and mm.group(1) not in MOTS_CLES and f.startswith("src/main") and "(" in l \
                    and not re.match(r"^\s*(return|throw|new)\b", l) and "=" not in l.split("(")[0]:
                nom = mm.group(1)
                # Constructeur : même nom que le type courant.
                if re.match(rf"^\s*(?:(?:public|protected|private)\s+)?{nom}\s*\(", l):
                    continue
                methodes.append({"fichier": f, "ligne": i + 1, "nom": nom,
                                 "framework": bool(ANNOT_FRAMEWORK.search("\n".join(src[max(0, i - 3):i])))})
    return types, methodes


def references(arbre: Path) -> dict[str, list[tuple[str, int, str]]]:
    """Index des sources java : fichier -> lignes."""
    idx = {}
    for p in arbre.glob("src/**/*.java"):
        rel = str(p.relative_to(arbre))
        idx[rel] = p.read_text().splitlines()
    return idx


def code_mort(arbre: Path, types: list[dict], methodes: list[dict]) -> dict:
    idx = references(arbre)
    mortes, test_seul = [], []
    for m in methodes:
        if m["framework"]:
            continue
        rx = re.compile(rf"(\.|::|\b){re.escape(m['nom'])}\s*\(|::{re.escape(m['nom'])}\b")
        main = test = 0
        for f, lignes in idx.items():
            for n, l in enumerate(lignes, 1):
                if f == m["fichier"] and n == m["ligne"]:
                    continue
                if rx.search(l) or (re.search(rf"\b{re.escape(m['nom'])}\s*\(", l) and not MOTIF_METHODE.match(l)):
                    if f.startswith("src/main"):
                        main += 1
                    else:
                        test += 1
        if main == 0 and test == 0:
            mortes.append(f"{m['fichier']}:{m['ligne']} {m['nom']}")
        elif main == 0:
            test_seul.append(f"{m['fichier']}:{m['ligne']} {m['nom']}")
    classes_mortes = []
    for t in types:
        if t["zone"] != "main" or t["spring"]:
            continue
        rx = re.compile(rf"\b{re.escape(t['nom'])}\b")
        n = sum(1 for f, lignes in idx.items() for k, l in enumerate(lignes, 1)
                if rx.search(l) and not (f == t["fichier"]))
        if n == 0:
            classes_mortes.append(f"{t['fichier']}:{t['ligne']} {t['nom']}")
    return {"methodes_jamais_appelees": mortes, "methodes_appelees_seulement_par_tests": test_seul,
            "types_jamais_references": classes_mortes}


def interfaces_une_impl(arbre: Path, types: list[dict]) -> list[dict]:
    idx = references(arbre)
    out = []
    for t in types:
        if t["genre"] != "interface" or t["zone"] != "main":
            continue
        rx = re.compile(rf"\bimplements\b[^{{]*\b{re.escape(t['nom'])}\b")
        impl_main = sum(1 for f, l in idx.items() if f.startswith("src/main") and rx.search("\n".join(l)))
        impl_test = sum(1 for f, l in idx.items() if f.startswith("src/test") and rx.search("\n".join(l)))
        out.append({"nom": t["nom"], "fichier": f"{t['fichier']}:{t['ligne']}", "impl_main": impl_main,
                    "impl_test": impl_test})
    return out


def surefire(dossier: Path) -> dict:
    tot = {"tests": 0, "echecs": 0, "erreurs": 0}
    for x in dossier.glob("TEST-*.xml") if dossier.is_dir() else []:
        r = ET.parse(x).getroot()
        tot["tests"] += int(r.get("tests", 0))
        tot["echecs"] += int(r.get("failures", 0))
        tot["erreurs"] += int(r.get("errors", 0))
    return tot


def analyser_copie(copie: Path, base: dict, env: dict, travail: Path, diffs: Path | None, etiquette: str) -> dict:
    depart = sh(["git", "rev-list", "--max-parents=0", "HEAD"], copie).stdout.split()[0]
    m = NOM_COPIE.match(copie.name)
    ajout = lignes_ajoutees(copie, depart)
    arbre = travail / f"{etiquette}-{copie.name}"
    shutil.rmtree(arbre, ignore_errors=True)
    arbre.mkdir(parents=True)
    exporter(copie, "agent", arbre)
    if diffs:
        diffs.mkdir(parents=True, exist_ok=True)
        excl = [f":(exclude){e}" for e in EXCLUS]
        d = sh(["git", "diff", "--no-color", "--no-renames", depart, "agent", "--", ".", *excl], copie).stdout
        (diffs / f"{etiquette}-{copie.name}.diff").write_text(d)
    r = analyser_arbre(arbre, env)
    pmd = lire_pmd(r["pmd"], arbre)
    cc = complexite_totale(pmd)
    meth_cc = [x for x in complexites_methodes(pmd) if touche(ajout, x["fichier"], x["ligne"], x["ligne"])]
    pmd_nouv = [v for v in pmd if v["regle"] != "CyclomaticComplexity" and touche(ajout, v["fichier"], v["ligne"], v["fin"])]
    types, methodes = types_et_methodes(arbre, ajout)
    # Nouveau = absent du projet de départ (une ligne de déclaration modifiée ne fait pas un nouveau type).
    types = [t for t in types if t["nom"] not in set(base["types"])]
    methodes = [x for x in methodes if f"{x['fichier']}#{x['nom']}" not in set(base["methodes"])]
    tests = tests_ajoutes(arbre, ajout)
    java = {f: l for f, l in ajout.items() if f.endswith(".java")}

    def non_vides(zone: str) -> int:
        n = 0
        for f, ls in java.items():
            if f.startswith(zone):
                src = (arbre / f).read_text().splitlines()
                n += sum(1 for k in ls if k - 1 < len(src) and src[k - 1].strip())
        return n

    res = {
        "modele": etiquette.split("-")[0], "etiquette": etiquette, "copie": copie.name,
        "tache": m.group(1), "condition": m.group(2), "passage": int(m.group(3)),
        "compile": r["compile"], "tests": surefire(r["surefire"]),
        "fichiers_modifies": sorted(ajout), "fichiers_supprimes": fichiers_supprimes(copie, depart),
        "lignes_ajoutees": {"main": non_vides("src/main"), "test": non_vides("src/test"),
                            "autres": sum(len(v) for f, v in ajout.items() if not f.endswith(".java"))},
        "types_ajoutes": {g: sum(1 for t in types if t["genre"] == g and t["zone"] == "main")
                          for g in ("class", "interface", "record", "enum")},
        "types_ajoutes_test": sum(1 for t in types if t["zone"] == "test"),
        "types_detail": [f"{t['fichier']}:{t['ligne']} {t['genre']} {t['nom']}" for t in types],
        "interfaces": interfaces_une_impl(arbre, types),
        "complexite_totale_main": cc["main"], "complexite_ajoutee_main": cc["main"] - base["cc_main"],
        "methodes_touchees_cc": meth_cc,
        "pmd_nouveaux": pmd_nouv,
        "cpd_nouveaux": lire_cpd(r["cpd"], arbre, ajout),
        "spotbugs_nouveaux": lire_spotbugs(r["spotbugs"], ajout),
        "jacoco": lire_jacoco(r["jacoco"], ajout),
        "tests_ajoutes": tests,
        **code_mort(arbre, types, methodes),
    }
    if not r["compile"]:
        res["journal_maven"] = r["journal"]
    return res


def ligne_de_base(copie: Path, env: dict, travail: Path) -> dict:
    depart = sh(["git", "rev-list", "--max-parents=0", "HEAD"], copie).stdout.split()[0]
    arbre = travail / "depart"
    shutil.rmtree(arbre, ignore_errors=True)
    arbre.mkdir(parents=True)
    exporter(copie, depart, arbre)
    r = analyser_arbre(arbre, env)
    pmd = lire_pmd(r["pmd"], arbre)
    tous = {str(f.relative_to(arbre)): set(range(1, len(f.read_text().splitlines()) + 1))
            for f in arbre.glob("src/**/*.java")}
    types, methodes = types_et_methodes(arbre, tous)
    return {"cc_main": complexite_totale(pmd)["main"],
            "types": sorted({t["nom"] for t in types}),
            "methodes": sorted({f"{m['fichier']}#{m['nom']}" for m in methodes}),
            "pmd_hors_cc": sum(1 for v in pmd if v["regle"] != "CyclomaticComplexity"),
            "spotbugs": len(list(ET.parse(r["spotbugs"]).getroot().iter("BugInstance"))) if r["spotbugs"].exists() else None,
            "tests": surefire(r["surefire"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--copies", action="append", required=True, help="etiquette=dossier (contient T01-A-1, …)")
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--diffs", default=None)
    ap.add_argument("--java-home", default=os.environ.get("JAVA_HOME"))
    ap.add_argument("--travail", default=None)
    a = ap.parse_args()
    env = dict(os.environ)
    if a.java_home:
        env["JAVA_HOME"] = a.java_home
        env["PATH"] = str(Path(a.java_home) / "bin") + os.pathsep + env["PATH"]
    travail = Path(a.travail or tempfile.mkdtemp(prefix="aveugle-analyse-"))
    copies = []
    for c in a.copies:
        etiq, dossier = c.split("=", 1)
        for p in sorted(Path(dossier).rglob("T[0-9][0-9]-*-*")):
            if p.is_dir() and NOM_COPIE.match(p.name) and (p / ".git").exists():
                copies.append((etiq, p))
    base = ligne_de_base(copies[0][1], env, travail)
    print("ligne de base :", base)
    sortie = Path(a.sortie)
    deja = set()
    if sortie.exists():
        deja = {(j["etiquette"], j["copie"]) for j in map(json.loads, sortie.read_text().splitlines())}
    for etiq, p in copies:
        if (etiq, p.name) in deja:
            continue
        if sh(["git", "rev-parse", "-q", "--verify", "agent"], p).returncode != 0:
            print(f"{etiq} {p.name} : pas de tag agent, ignorée")
            continue
        res = analyser_copie(p, base, env, travail, Path(a.diffs) if a.diffs else None, etiq)
        res["ligne_de_base"] = {k: v for k, v in base.items() if k not in ("types", "methodes")}
        with sortie.open("a") as f:
            f.write(json.dumps(res, ensure_ascii=False) + "\n")
        print(f"{etiq} {p.name} : +{res['lignes_ajoutees']} cc+{res['complexite_ajoutee_main']} "
              f"pmd={len(res['pmd_nouveaux'])} cpd={len(res['cpd_nouveaux'])} sb={len(res['spotbugs_nouveaux'])} "
              f"tests={len(res['tests_ajoutes'])} jacoco={res['jacoco']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
