"""Compte les violations des règles anti-slop et l'état des tests dans une copie du projet.

Utilisé par lancer.py après le passage de l'agent. Bibliothèque standard seulement.

Principe : on remet dans la copie les classes de règles d'origine (l'agent a pu les modifier,
ou elles n'existaient pas dans les conditions A et B), puis Maven lance :
  1. les tests d'architecture (ProjectArchTest, TestSourcesArchTest) -> violations par règle ;
  2. les autres tests (tests fonctionnels du projet + ceux écrits par l'agent) -> réussis / échoués.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

REGLES_DIR = Path("src/test/java/io/github/mekkiamiri/ratchet/rules")
# Fichiers remis depuis le projet d'origine avant de compter.
FICHIERS_REGLES = ["AntiSlopRules.java", "ProjectArchTest.java", "TestSourcesArchTest.java"]
TESTS_ARCHI = "ProjectArchTest,TestSourcesArchTest"

MOTIF_VIOLATION = re.compile(r"Rule 'R(\d{2})\b.*?' was violated \((\d+) times?\)", re.S)


def violations_depuis_texte(texte: str) -> dict[str, int]:
    """Extrait {"R08": 2, ...} des messages d'échec ArchUnit."""
    compte: dict[str, int] = {}
    for num, n in MOTIF_VIOLATION.findall(texte):
        cle = "R" + num
        compte[cle] = compte.get(cle, 0) + int(n)
    return compte


def lire_rapports(dossier: Path) -> tuple[str, dict[str, int]]:
    """Concatène les messages d'échec et compte les tests des rapports Surefire XML."""
    textes: list[str] = []
    totaux = {"tests": 0, "echecs": 0, "erreurs": 0, "ignores": 0}
    if not dossier.is_dir():
        return "", totaux
    for xml in sorted(dossier.glob("TEST-*.xml")):
        racine = ET.parse(xml).getroot()
        totaux["tests"] += int(racine.get("tests", 0))
        totaux["echecs"] += int(racine.get("failures", 0))
        totaux["erreurs"] += int(racine.get("errors", 0))
        totaux["ignores"] += int(racine.get("skipped", 0))
        for el in racine.iter():
            if el.tag in ("failure", "error"):
                # Le message ArchUnit est souvent répété dans l'attribut et dans le corps : un seul des deux.
                corps = el.text or ""
                textes.append(corps if MOTIF_VIOLATION.search(corps) else (el.get("message") or ""))
    return "\n".join(textes), totaux


def _maven(copie: Path, args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess:
    rapports = copie / "target" / "surefire-reports"
    if rapports.exists():
        shutil.rmtree(rapports)
    return subprocess.run(["mvn", "-o", "-q", "-B", *args], cwd=copie, env=env,
                          capture_output=True, text=True, timeout=900)


def compter(copie: Path, origine: Path, java_home: str | None = None) -> dict:
    env = dict(os.environ)
    if java_home:
        env["JAVA_HOME"] = java_home
        env["PATH"] = str(Path(java_home) / "bin") + os.pathsep + env.get("PATH", "")
    (copie / REGLES_DIR).mkdir(parents=True, exist_ok=True)
    for nom in FICHIERS_REGLES:
        shutil.copy2(origine / REGLES_DIR / nom, copie / REGLES_DIR / nom)

    archi = _maven(copie, ["test", f"-Dtest={TESTS_ARCHI}", "-Dsurefire.failIfNoSpecifiedTests=false"], env)
    texte, _ = lire_rapports(copie / "target" / "surefire-reports")
    compile_ok = "COMPILATION ERROR" not in (archi.stdout + archi.stderr)
    violations = violations_depuis_texte(texte)

    # Tests fonctionnels : on retire les règles et les mauvais exemples volontaires du catalogue,
    # puis Surefire tourne avec ses motifs par défaut (comme en vrai : un test mal nommé ne tourne pas).
    shutil.rmtree(copie / REGLES_DIR, ignore_errors=True)
    shutil.rmtree(copie / "src/test/java/io/github/mekkiamiri/slopexamples", ignore_errors=True)
    fonc = _maven(copie, ["test"], env)
    _, totaux = lire_rapports(copie / "target" / "surefire-reports")
    return {
        "compile": compile_ok,
        "violations": violations,
        "violations_total": sum(violations.values()),
        "tests_fonctionnels": totaux,
        "tests_fonctionnels_ok": fonc.returncode == 0,
    }
