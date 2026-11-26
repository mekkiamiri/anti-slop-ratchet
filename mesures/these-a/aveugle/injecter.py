"""Injection de défauts : un « score de mutation » pour le harnais.

Pour chaque défaut de defauts.json (remplacements exacts de texte dans une copie produite par l'agent) :
  1. exporte l'arbre « agent » de la copie (propre, sans règles), puis applique les remplacements ;
  2. les 11 règles : compter.py remet les règles d'origine et lance ProjectArchTest + TestSourcesArchTest
     (exactement ce que le hook de la condition C lance), puis les tests fonctionnels (projet + agent) ;
  3. PMD/CPD/SpotBugs (même configuration qu'analyser.py) : un défaut est « vu » si un avertissement
     tombe dans la zone injectée (lignes du texte inséré, ±1) et n'existait pas avant l'injection.
Sortie : une ligne JSON par défaut.

Usage : python3 injecter.py --defauts defauts.json --copies sonnet-A=<dossier> ... --sortie defauts.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parents[2]
sys.path.insert(0, str(ICI))
sys.path.insert(0, str(RACINE / "mesures"))
import analyser as an  # noqa: E402
import compter as compteur  # noqa: E402


def trouver_copie(copies: dict[str, Path], ref: str) -> Path:
    etiq, nom = ref.split("/")
    res = [p for p in copies[etiq].rglob(nom) if p.is_dir() and (p / ".git").exists()]
    if not res:
        raise SystemExit(f"copie introuvable : {ref}")
    return res[0]


def appliquer(arbre: Path, remplacements: list[dict]) -> dict[str, set[int]]:
    """Applique les remplacements ; renvoie les lignes de la zone injectée par fichier (±1)."""
    zones: dict[str, set[int]] = {}
    for r in remplacements:
        f = arbre / r["fichier"]
        if r.get("nouveau_fichier"):
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(r["apres"])
            zones.setdefault(r["fichier"], set()).update(range(1, r["apres"].count("\n") + 2))
            continue
        s = f.read_text()
        if s.count(r["avant"]) != 1:
            raise SystemExit(f"{r['fichier']} : texte à remplacer trouvé {s.count(r['avant'])} fois")
        debut = s[:s.index(r["avant"])].count("\n") + 1
        s = s.replace(r["avant"], r["apres"])
        f.write_text(s)
        fin = debut + r["apres"].count("\n")
        zones.setdefault(r["fichier"], set()).update(range(max(1, debut - 1), fin + 2))
    return zones


def constats(arbre: Path, env: dict, fichiers: set[str]) -> dict:
    """Avertissements des outils sur les fichiers touchés par l'injection, comptés par (outil, règle, fichier).

    On compare des comptes et pas des lignes : l'injection décale les lignes, et certains outils signalent
    la déclaration de méthode plutôt que la ligne fautive (ex. UnitTestShouldIncludeAssert)."""
    r = an.analyser_arbre(arbre, env)
    tout = {f: set(range(1, 100000)) for f in fichiers}
    cles: dict[str, int] = {}

    def plus(cle: str) -> None:
        cles[cle] = cles.get(cle, 0) + 1

    for v in an.lire_pmd(r["pmd"], arbre):
        if v["regle"] != "CyclomaticComplexity" and v["fichier"] in fichiers:
            plus(f"pmd {v['regle']} {v['fichier'].rsplit('/', 1)[-1]}")
    for d in an.lire_cpd(r["cpd"], arbre, tout):
        plus("cpd " + " / ".join(sorted(o.rsplit("/", 1)[-1].split(":")[0] for o in d["occurrences"])))
    for b in an.lire_spotbugs(r["spotbugs"], tout):
        plus(f"spotbugs {b['type']} {b['fichier'].rsplit('/', 1)[-1]}")
    return {"cles": cles, "compile": r["compile"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--defauts", required=True)
    ap.add_argument("--copies", action="append", required=True)
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--seulement", default=None)
    ap.add_argument("--java-home", default=os.environ.get("JAVA_HOME"))
    a = ap.parse_args()
    env = dict(os.environ)
    if a.java_home:
        env["JAVA_HOME"] = a.java_home
        env["PATH"] = str(Path(a.java_home) / "bin") + os.pathsep + env["PATH"]
    copies = {c.split("=", 1)[0]: Path(c.split("=", 1)[1]) for c in a.copies}
    defauts = json.loads(Path(a.defauts).read_text())["defauts"]
    if a.seulement:
        defauts = [d for d in defauts if d["id"] in a.seulement.split(",")]
    travail = Path(tempfile.mkdtemp(prefix="aveugle-inject-"))
    for d in defauts:
        copie = trouver_copie(copies, d["copie"])
        # Avant injection : mêmes analyses sur la même zone (ce qui y était déjà signalé ne compte pas).
        avant = travail / f"{d['id']}-avant"
        avant.mkdir()
        an.exporter(copie, "agent", avant)
        apres = travail / f"{d['id']}-apres"
        apres.mkdir()
        an.exporter(copie, "agent", apres)
        zones = appliquer(apres, d["remplacements"])
        c_avant = constats(avant, env, set(zones))
        compte = compteur.compter(apres, RACINE, a.java_home)  # règles, puis tests (règles retirées ensuite)
        c_apres = constats(apres, env, set(zones))

        def nouveaux(outil: str) -> list[str]:
            return [k[len(outil) + 1:] for k, n in c_apres["cles"].items()
                    if k.startswith(outil + " ") and n > c_avant["cles"].get(k, 0)]

        ligne = {
            "id": d["id"], "nom": d["nom"], "famille": d["famille"], "copie": d["copie"],
            "compile": compte["compile"],
            "regles_11": compte["violations"],
            "vu_par_regles": compte["violations_total"] > 0,
            "pmd": nouveaux("pmd"), "cpd": nouveaux("cpd"), "spotbugs": nouveaux("spotbugs"),
            "tests": compte["tests_fonctionnels"],
            "vu_par_tests": not compte["tests_fonctionnels_ok"],
        }
        ligne["vu_par_outils"] = bool(ligne["pmd"] or ligne["cpd"] or ligne["spotbugs"])
        ligne["vu_par_quelquun"] = ligne["vu_par_regles"] or ligne["vu_par_outils"] or ligne["vu_par_tests"]
        with open(a.sortie, "a") as f:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
        print(f"{d['id']} {d['nom']} : règles={compte['violations']} pmd={ligne['pmd']} cpd={ligne['cpd']} "
              f"sb={ligne['spotbugs']} tests_rouges={ligne['vu_par_tests']}")
        shutil.rmtree(avant, ignore_errors=True)
        shutil.rmtree(apres, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
