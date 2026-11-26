"""Banc de mesure du talk : un prompt se suggère, une règle s'impose.

Pour chaque tâche (taches.json), chaque condition et chaque passage :
  1. copie neutre du projet dans un dossier jetable (sans README, RATCHET.md, docs, slides, mesures) ;
  2. préparation de la condition :
       A  rien      : ni règles, ni hook, ni consignes ;
       B  consignes : les 11 remarques écrites dans CLAUDE.md (consignes-CLAUDE.md), sans règles ni hook ;
       C  règles    : les règles ArchUnit et le hook (.claude/settings.json), sans CLAUDE.md ;
  3. l'agent fait la tâche en mode non interactif (commande configurable, --agent-cmd) ;
  4. compter.py remet les règles d'origine et compte les violations et les tests.
Résultat : une ligne JSON par passage dans mesures/resultats/<date>.jsonl.

Usage :
  python3 mesures/lancer.py --taches T01,T02 --conditions A,B,C --passages 3 --java-home <JDK 21+>
  python3 mesures/lancer.py --essai-a-blanc   # sans modèle : un faux agent écrit une violation connue
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ICI = Path(__file__).resolve().parent
RACINE = ICI.parent
sys.path.insert(0, str(ICI))
import compter as compteur  # noqa: E402

A_RETIRER = ["README.md", "RATCHET.md", "docs", "slides", "mesures", ".github", "target", "LICENSE",
             "src/test/java/io/github/mekkiamiri/ratchet/rules/CatalogPageTest.java"]
REGLES = ["src/test/java/io/github/mekkiamiri/ratchet/rules", "src/test/java/io/github/mekkiamiri/slopexamples", ".claude"]
OUTILS = "Read Edit Write Glob Grep Bash(mvn:*)"
CONSIGNE_FIN = ("\n\nTravaille seul, sans poser de question. Le projet compile avec `mvn -o -q test` "
                "(hors ligne). Quand la tâche est faite et que les tests passent, arrête-toi.")


def copie_neutre(dest: Path, projet: str = "propre") -> None:
    fichiers = subprocess.run(["git", "ls-files", "-z"], cwd=RACINE, capture_output=True, check=True).stdout
    for rel in filter(None, fichiers.decode().split("\0")):
        src = RACINE / rel
        if src.is_file():
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest / rel)
    for rel in A_RETIRER:
        p = dest / rel
        shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
    if projet == "sale":
        sale = ICI / "projet-sale"
        for src in sale.rglob("*.java"):
            cible = dest / src.relative_to(sale)
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, cible)
        # Les commentaires qui annoncent le sujet du talk sont retirés (l'agent ne doit pas le deviner).
        app = dest / "src/main/java/io/github/mekkiamiri/ratchet/ShopApplication.java"
        app.write_text("\n".join(l for l in app.read_text().splitlines() if "anti-slop" not in l) + "\n")


def preparer(dest: Path, condition: str) -> None:
    if condition in ("A", "B"):
        for rel in REGLES:
            shutil.rmtree(dest / rel, ignore_errors=True)
    if condition == "B":
        shutil.copy2(ICI / "consignes-CLAUDE.md", dest / "CLAUDE.md")
    # Le hook a besoin d'un dépôt git (empreinte de git diff) ; l'agent part d'un état propre.
    for cmd in (["git", "init", "-q"], ["git", "add", "-A"],
                ["git", "-c", "user.email=banc@exemple.invalid", "-c", "user.name=banc", "commit", "-q", "-m", "départ"]):
        subprocess.run(cmd, cwd=dest, check=True, capture_output=True)


def lancer_agent(dest: Path, texte: str, agent_cmd: str, modele: str | None, env: dict) -> dict:
    cmd = shlex.split(agent_cmd) + ["-p", texte + CONSIGNE_FIN, "--output-format", "json",
                                    "--setting-sources", "project", "--permission-mode", "acceptEdits",
                                    "--allowedTools", OUTILS]
    if modele:
        cmd += ["--model", modele]
    debut = time.monotonic()
    p = subprocess.run(cmd, cwd=dest, env=env, capture_output=True, text=True, timeout=1800)
    duree = round(time.monotonic() - debut, 1)
    try:
        sortie = json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "code": p.returncode, "duree_s": duree, "erreur": (p.stderr or p.stdout)[-500:]}
    tokens = sortie.get("usage") or {}
    if sortie.get("is_error") and not tokens.get("output_tokens"):
        # Erreur d'accès au modèle (identifiants expirés, quota) : pas un résultat, à relancer.
        return {"ok": False, "invalide": True, "code": p.returncode, "duree_s": duree,
                "erreur": (sortie.get("result") or "")[:300]}
    return {"ok": not sortie.get("is_error", False), "code": p.returncode, "duree_s": duree,
            "cout_usd": sortie.get("total_cost_usd"), "tours": sortie.get("num_turns"),
            "modeles_servis": sorted((sortie.get("modelUsage") or {}).keys()),
            "tokens": sortie.get("usage"), "resume_agent": (sortie.get("result") or "")[-400:]}


FAUX_AGENT = """#!/bin/sh
# Faux agent de l'essai à blanc : écrit une violation connue de R08 et de R04, sans appeler de modèle.
mkdir -p src/main/java/io/github/mekkiamiri/ratchet/order/domain
cat > src/main/java/io/github/mekkiamiri/ratchet/order/domain/RemiseEssai.java <<'J'
package io.github.mekkiamiri.ratchet.order.domain;
import java.math.BigDecimal;
public final class RemiseEssai {
    private RemiseEssai() {}
    public static BigDecimal taux() { System.out.println("remise"); return new BigDecimal(0.1); }
}
J
echo '{"is_error": false, "result": "faux agent", "total_cost_usd": 0, "num_turns": 0, "modelUsage": {}}'
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--taches", default="all")
    ap.add_argument("--conditions", default="A,B,C")
    ap.add_argument("--passages", type=int, default=1)
    ap.add_argument("--agent-cmd", default=os.environ.get("BANC_AGENT_CMD", "claude"))
    ap.add_argument("--modele", default=None)
    ap.add_argument("--java-home", default=os.environ.get("BANC_JAVA_HOME"))
    ap.add_argument("--garder", action="store_true", help="garder les copies (pour relire les diffs)")
    ap.add_argument("--dossier-copies", default=None,
                    help="dossier où créer les copies (défaut : dossier temporaire) ; utile avec --garder")
    ap.add_argument("--etiquette", default="",
                    help="suffixe du fichier de résultats (ex. --etiquette=-aveugle-sonnet), pour ne pas mélanger les campagnes")
    ap.add_argument("--essai-a-blanc", action="store_true")
    ap.add_argument("--projet", choices=["propre", "sale"], default="propre",
                    help="sale : le service et le contrôleur contiennent déjà 7 erreurs du catalogue (projet-sale/)")
    a = ap.parse_args()

    taches = json.loads((ICI / "taches.json").read_text())["taches"]
    if a.taches != "all":
        voulues = set(a.taches.split(","))
        taches = [t for t in taches if t["id"] in voulues]
    conditions = a.conditions.split(",")
    env = dict(os.environ)
    if a.java_home:
        env["JAVA_HOME"] = a.java_home
        env["PATH"] = str(Path(a.java_home) / "bin") + os.pathsep + env["PATH"]

    if a.dossier_copies:
        Path(a.dossier_copies).mkdir(parents=True, exist_ok=True)
    racine_runs = Path(tempfile.mkdtemp(prefix="banc-antislop-", dir=a.dossier_copies))
    if a.essai_a_blanc:
        faux = racine_runs / "faux-agent.sh"
        faux.write_text(FAUX_AGENT)
        faux.chmod(0o755)
        a.agent_cmd, taches, conditions, a.passages = str(faux), taches[:1], ["A"], 1

    suffixe = "-essai" if a.essai_a_blanc else ("-sale" if a.projet == "sale" else "")
    sortie = ICI / "resultats" / f"{dt.date.today().isoformat()}{suffixe}{a.etiquette}.jsonl"
    # Violations déjà présentes avant l'agent (0 pour le projet propre) : on compte ensuite les nouvelles.
    base_dir = racine_runs / "ligne-de-base"
    base_dir.mkdir()
    copie_neutre(base_dir, a.projet)
    preparer(base_dir, "A")
    depart = compteur.compter(base_dir, RACINE, a.java_home)["violations"]
    print(f"violations au départ ({a.projet}) : {depart}")
    shutil.rmtree(base_dir, ignore_errors=True)
    sortie.parent.mkdir(exist_ok=True)
    for t in taches:
        for c in conditions:
            for n in range(1, a.passages + 1):
                dest = racine_runs / f"{t['id']}-{c}-{n}"
                dest.mkdir()
                copie_neutre(dest, a.projet)
                preparer(dest, c)
                agent = lancer_agent(dest, t["texte"], a.agent_cmd, a.modele, env)
                if agent.get("invalide"):
                    print(f"{t['id']} {c} #{n} : INVALIDE (accès au modèle) : {agent['erreur'][:120]}")
                    shutil.rmtree(dest, ignore_errors=True)
                    continue
                if a.garder:
                    # Instantané du code rendu par l'agent, avant que le compteur ne touche à la copie
                    # (il remet puis retire les règles) : le diff départ..agent reste relisible.
                    subprocess.run(["git", "add", "-A"], cwd=dest, capture_output=True)
                    subprocess.run(["git", "-c", "user.email=banc@exemple.invalid", "-c", "user.name=banc",
                                    "commit", "-q", "--allow-empty", "-m", "agent"], cwd=dest, capture_output=True)
                    subprocess.run(["git", "tag", "agent"], cwd=dest, capture_output=True)
                mesure = compteur.compter(dest, RACINE, a.java_home)
                nouvelles = {r: n_ - depart.get(r, 0) for r, n_ in mesure["violations"].items()
                             if n_ - depart.get(r, 0) > 0}
                ligne = {"date": dt.datetime.now().isoformat(timespec="seconds"), "projet": a.projet, "tache": t["id"],
                         "zone": t["zone"], "condition": c, "passage": n, "modele_demande": a.modele, "agent": agent, **mesure,
                         "violations_depart": depart, "violations_nouvelles": nouvelles,
                         "violations_nouvelles_total": sum(nouvelles.values())}
                with sortie.open("a") as f:
                    f.write(json.dumps(ligne, ensure_ascii=False) + "\n")
                print(f"{t['id']} {c} #{n} : violations={mesure['violations']} nouvelles={nouvelles} "
                      f"tests_ok={mesure['tests_fonctionnels_ok']} agent_ok={agent['ok']} {agent.get('duree_s')} s")
                if not a.garder:
                    shutil.rmtree(dest, ignore_errors=True)
    print(f"résultats : {sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
