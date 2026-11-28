"""Revue croisée : combien des défauts trouvés par la revue le harnais voit-il ?

Entrées (dans ce dossier) :
  agent-de-revue/constats.json   constats de l'agent de revue (gsd-code-reviewer), diffs anonymes A..K
  juge-aveugle/jugement.json     notes et défauts du juge à l'aveugle (grille-juge.md)
  correspondance.json            lettre -> copie (ouverte après les deux revues)
  harnais/*.json                 sortie de harness-mutant sur chaque copie (témoin = 11 règles + tests)
  ../aveugle/mesures.jsonl       avertissements PMD / CPD / SpotBugs nouveaux de chaque copie
  ../aveugle/revue.json          l'ancienne revue simulée (historique)

Règles de croisement (mécaniques) :
  - deux constats sont « le même défaut » s'ils portent sur la même copie, le même fichier et des lignes
    qui se chevauchent à 3 lignes près ;
  - un défaut est « vu par les 11 règles » si une règle a sonné sur la copie (témoin rouge) ;
  - « vu par PMD/CPD/SpotBugs » si un avertissement nouveau tombe dans le même fichier à 2 lignes près
    ET dit la même chose (liste MEME_SENS, vide par défaut : chaque recouvrement est imprimé pour être jugé) ;
  - « vu par les tests » si un test est rouge sur la copie (témoin rouge).

Usage : python3 croiser.py   (écrit croisement.json et affiche le résumé)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ICI = Path(__file__).resolve().parent
AVEUGLE = ICI.parent / "aveugle"
POIDS = {"critique": 5, "majeure": 3, "mineure": 1, "style": 0}
# Recouvrements outil/constat jugés « même sens » après lecture (clé : source#index, valeur : règle de l'outil).
MEME_SENS: dict[str, str] = {}


def lignes(txt: str) -> tuple[int, int]:
    nums = [int(n) for n in re.findall(r"\d+", txt or "")]
    return (min(nums), max(nums)) if nums else (0, 0)


def recouvre(a: tuple[int, int], b: tuple[int, int], marge: int) -> bool:
    return a[0] - marge <= b[1] and b[0] - marge <= a[1]


def base(f: str) -> str:
    return f.rsplit("/", 1)[-1]


def charger() -> list[dict]:
    corr = json.loads((ICI / "correspondance.json").read_text())
    defauts = []
    for i, c in enumerate(json.loads((ICI / "agent-de-revue/constats.json").read_text())["constats"]):
        defauts.append({"source": "agent", "cle": f"agent#{i}", "diff": c["diff"], "copie": corr[c["diff"]],
                        "fichier": c["fichier"], "lignes": lignes(c["lignes"]), "gravite": c["gravite"],
                        "categorie": c["categorie"], "texte": c["texte"]})
    for d in json.loads((ICI / "juge-aveugle/jugement.json").read_text())["diffs"]:
        for i, c in enumerate(d["defauts"]):
            defauts.append({"source": "juge", "cle": f"juge#{d['diff']}{i}", "diff": d["diff"],
                            "copie": corr[d["diff"]], "fichier": c["fichier"], "lignes": lignes(c["lignes"]),
                            "gravite": c["gravite"], "categorie": c["categorie"], "texte": c["texte"]})
    return defauts


def avertissements() -> dict[str, list[dict]]:
    res: dict[str, list[dict]] = {}
    for l in (AVEUGLE / "mesures.jsonl").read_text().splitlines():
        m = json.loads(l)
        cle = f"{m['etiquette']}/{m['copie']}"
        res[cle] = [{"outil": "pmd", **w} for w in m["pmd_nouveaux"]] + \
                   [{"outil": "spotbugs", **w} for w in m["spotbugs_nouveaux"]] + \
                   [{"outil": "cpd", **w} for w in m["cpd_nouveaux"]]
    return res


def temoins() -> dict[str, dict]:
    """Copie -> témoin de harness-mutant (vert = 0 règle violée et tous les tests verts)."""
    res = {}
    for f in sorted((ICI / "harnais").glob("*.json")):
        s = json.loads(f.read_text())
        res[f.stem] = s  # nom du fichier : copie avec « - » au lieu de « / »
    return res


def main() -> int:
    defauts = charger()
    warn = avertissements()
    harn = temoins()
    # 1. Regroupement en défauts uniques (agent x juge).
    groupes: list[list[dict]] = []
    for d in defauts:
        for g in groupes:
            if any(x["copie"] == d["copie"] and base(x["fichier"]) == base(d["fichier"])
                   and recouvre(x["lignes"], d["lignes"], 3) and x["source"] != d["source"] for x in g):
                g.append(d)
                break
        else:
            groupes.append([d])
    # 2. Qui le voit ?
    recouvrements = []
    uniques = []
    for g in groupes:
        copie = g[0]["copie"]
        s = harn.get(copie.replace("/", "-"))
        temoin_vert = s is not None and "erreur" not in s
        vu_outil = []
        for d in g:
            for w in warn.get(copie, []):
                if base(w["fichier"]) == base(d["fichier"]) and recouvre((w["ligne"], w.get("fin", w["ligne"])), d["lignes"], 2):
                    recouvrements.append({"defaut": d["cle"], "texte": d["texte"][:120], "outil": w["outil"],
                                          "regle": w.get("regle") or w.get("type"), "ligne": w["ligne"]})
                    if MEME_SENS.get(d["cle"]):
                        vu_outil.append(MEME_SENS[d["cle"]])
        grav = max((x["gravite"] for x in g), key=lambda k: POIDS[k])
        uniques.append({
            "copie": copie, "diff": g[0]["diff"], "fichier": g[0]["fichier"], "gravite_max": grav,
            "sources": sorted({x["source"] for x in g}), "textes": [f"[{x['source']}] {x['texte']}" for x in g],
            "vu_par_regles": bool(s) and not temoin_vert,
            "vu_par_outils": sorted(set(vu_outil)),
            "vu_par_tests": bool(s) and not temoin_vert,
            "temoin_mesure": s is not None,
        })
    # 3. Historique : le défaut figurait-il dans l'ancienne revue simulée (revue.json) ?
    anciennes = []
    for c in json.loads((AVEUGLE / "revue.json").read_text())["copies"]:
        for r in c["remarques"]:
            for ou in r["ou"]:
                f, _, l = ou.partition(":")
                anciennes.append((c["copie"], base(f), lignes(l)))
    for u, g in zip(uniques, groupes):
        u["dans_l_ancienne_revue"] = any(c == u["copie"] and f == base(x["fichier"]) and recouvre(l, x["lignes"], 3)
                                         for x in g for c, f, l in anciennes)
    for u in uniques:
        u["vu_par_harnais"] = u["vu_par_regles"] or bool(u["vu_par_outils"]) or u["vu_par_tests"]
    fond = [u for u in uniques if u["gravite_max"] != "style"]
    res = {
        "constats_agent": sum(1 for d in defauts if d["source"] == "agent"),
        "constats_juge": sum(1 for d in defauts if d["source"] == "juge"),
        "defauts_uniques": len(uniques),
        "dont_style": len(uniques) - len(fond),
        "trouves_par_les_deux": sum(1 for u in uniques if len(u["sources"]) == 2),
        "majeurs_uniques": sum(1 for u in uniques if u["gravite_max"] in ("majeure", "critique")),
        "temoins_mesures": sum(1 for u in uniques if u["temoin_mesure"]),
        "vus_par_regles": sum(u["vu_par_regles"] for u in uniques),
        "vus_par_outils": sum(bool(u["vu_par_outils"]) for u in uniques),
        "vus_par_tests": sum(u["vu_par_tests"] for u in uniques),
        "vus_par_harnais": sum(u["vu_par_harnais"] for u in uniques),
        "deja_dans_l_ancienne_revue": sum(u["dans_l_ancienne_revue"] for u in uniques),
        "recouvrements_outil_a_juger": recouvrements,
        "defauts": uniques,
    }
    (ICI / "croisement.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n")
    for k, v in res.items():
        if k not in ("defauts", "recouvrements_outil_a_juger"):
            print(f"{k}: {v}")
    print("recouvrements outil / constat à juger :")
    for r in recouvrements:
        print(f"  {r['defaut']} {r['outil']} {r['regle']} l.{r['ligne']} : {r['texte']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
