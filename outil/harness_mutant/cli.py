"""Ligne de commande : harness-mutant --projet . --commande "mvn -o -q verify"."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from harness_mutant import __version__
from harness_mutant.sonde import candidats, charger_catalogue, diff_git, lignes_ajoutees, sonder


def rapport_texte(s: dict) -> str:
    if "erreur" in s:
        return f"ERREUR : {s['erreur']} (code {s['code']}).\n--- fin de la sortie ---\n{s['extrait']}"
    l = [f"Projet : {s['projet']} · harnais : « {s['commande']} » (témoin vert en {s['duree_temoin_s']:.0f} s)", ""]
    if not s["comptes"]:
        l.append("Aucun défaut du catalogue ne s'applique à ce projet : ajoutez un catalogue (--defauts).")
        return "\n".join(l)
    trous = [r for r in s["resultats"] if r["statut"] == "trou"]
    pluriel = "s" if s["attrapes"] > 1 else ""
    l.append(f"Votre harnais attrape {s['attrapes']} défaut{pluriel} sur {s['comptes']} ({s['score']} %).")
    if s["par_signal"]:
        l.append("  attrapés par : " + ", ".join(f"{k} {v}" for k, v in sorted(s["par_signal"].items(), key=lambda kv: -kv[1])))
    l.append("")
    titre = f"Les {len(trous)} trous" if len(trous) > 1 else f"{len(trous)} trou"
    l.append(f"{titre} (le défaut est entré, la commande est restée verte) :")
    for r in trous:
        l.append(f"  {r['id']}  {r['nom']}  ({r['fichier']}:{r['ligne']})")
        if r["pour_l_attraper"]:
            l.append(f"        pour l'attraper : {r['pour_l_attraper']}")
    attrapes = [r for r in s["resultats"] if r["statut"] == "attrape"]
    if attrapes:
        l.append("")
        l.append("Attrapés :")
        for r in attrapes:
            l.append(f"  {r['id']}  {r['nom']}  -> {', '.join(r['signaux'])}")
    if s["non_applicables"] or s["ne_compilent_pas"]:
        l.append("")
        if s["non_applicables"]:
            l.append(f"Non applicables ici (motif absent) : {', '.join(s['non_applicables'])}")
        if s["ne_compilent_pas"]:
            l.append(f"Ne compilent pas ici (non comptés, comme les mutants non viables de PIT) : {', '.join(s['ne_compilent_pas'])}")
    return "\n".join(l)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="harness-mutant",
        description="Injecte des défauts réalistes dans une copie du projet, lance votre harnais "
                    "(une commande : vert = code de sortie 0) et compte ce qu'il attrape.")
    ap.add_argument("--projet", default=".", help="dossier du projet (copié, jamais modifié)")
    ap.add_argument("--commande", required=True, help='votre harnais, ex. "mvn -o -q verify"')
    ap.add_argument("--defauts", action="append", help="catalogue JSON (répétable) ; défaut : catalogue Java livré")
    ap.add_argument("--exclure", action="append", default=[], help="motif de chemin à ne pas modifier (répétable), ex. '*/generated/*'")
    ap.add_argument("--base", help="ne viser que les lignes changées depuis cette référence git (ex. main) : le code de l'agent")
    ap.add_argument("--diff", help="idem à partir d'un fichier de diff unifié (ex. sortie de git diff)")
    ap.add_argument("--seulement", help="liste d'identifiants, ex. J01,J07")
    ap.add_argument("--delai", type=int, default=900, help="délai max d'une exécution, en secondes")
    ap.add_argument("--essais", type=int, default=3, help="endroits essayés par défaut si le premier ne compile pas")
    ap.add_argument("--json", help="écrit le résultat complet dans ce fichier")
    ap.add_argument("--seuil", type=int, help="code de sortie 1 si le score (en %%) est sous ce seuil (pour la CI)")
    ap.add_argument("--lister", action="store_true", help="montre où chaque défaut s'appliquerait, sans rien lancer")
    ap.add_argument("--silencieux", action="store_true", help="n'affiche que le rapport final")
    ap.add_argument("--version", action="version", version=f"harness-mutant {__version__}")
    a = ap.parse_args(argv)

    projet = Path(a.projet)
    if not projet.is_dir():
        ap.error(f"projet introuvable : {projet}")
    # Réglages du projet (facultatif) : .harness-mutant.json {"exclure": [...], "defauts": [...]}
    reglages = projet / ".harness-mutant.json"
    if reglages.is_file():
        r = json.loads(reglages.read_text("utf-8"))
        a.exclure = list(r.get("exclure", [])) + a.exclure
        if not a.defauts and r.get("defauts"):
            a.defauts = [str(projet / c) for c in r["defauts"]]
    defauts = charger_catalogue(a.defauts)
    if a.seulement:
        voulus = set(a.seulement.split(","))
        defauts = [d for d in defauts if d.id in voulus]
    cibles = None
    if a.base and a.diff:
        ap.error("--base ou --diff, pas les deux")
    if a.base:
        cibles = lignes_ajoutees(diff_git(projet, a.base))
    elif a.diff:
        cibles = lignes_ajoutees(Path(a.diff).read_text("utf-8"))
    if a.lister:
        for d in defauts:
            cands = candidats(projet, d, a.exclure, cibles)
            ou = f"{cands[0].fichier}:{cands[0].ligne}  {cands[0].avant.strip()[:60]!r} -> {cands[0].apres.strip()[:60]!r}" if cands else "non applicable"
            print(f"{d.id}  {d.nom}  [{len(cands)} endroit(s)]  {ou}")
        return 0
    journal = (lambda *_: None) if a.silencieux else (lambda m: print(m, file=sys.stderr, flush=True))
    s = sonder(projet, a.commande, defauts, a.exclure, a.delai, a.essais, journal, cibles)
    print(rapport_texte(s))
    if a.json:
        Path(a.json).write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", "utf-8")
    if "erreur" in s:
        return 2
    if a.seuil is not None and s["score"] is not None and s["score"] < a.seuil:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
