"""Agrège mesures.jsonl (analyser.py), les résultats des passages, revue.json et defauts-resultats.jsonl
en tableaux Markdown (sortie standard) et synthese.json."""
from __future__ import annotations

import json
import statistics as st
from collections import defaultdict
from pathlib import Path

ICI = Path(__file__).resolve().parent
RES = ICI.parents[1] / "resultats"


def charger(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def moy(xs):
    xs = list(xs)
    return round(st.mean(xs), 2) if xs else None


def groupe_mesures(m: list[dict]) -> dict:
    tests = [t for x in m for t in x["tests_ajoutes"]]
    exe = sum(x["jacoco"]["lignes_executables_ajoutees"] for x in m)
    cov = sum(x["jacoco"]["lignes_couvertes_ajoutees"] for x in m)
    return {
        "copies": len(m),
        "lignes_main": moy(x["lignes_ajoutees"]["main"] for x in m),
        "lignes_test": moy(x["lignes_ajoutees"]["test"] for x in m),
        "nouveaux_types_main": moy(sum(x["types_ajoutes"].values()) for x in m),
        "nouvelles_interfaces": sum(x["types_ajoutes"]["interface"] for x in m),
        "interfaces_une_impl": sum(1 for x in m for i in x["interfaces"] if i["impl_main"] == 1),
        "cc_ajoutee": moy(x["complexite_ajoutee_main"] for x in m),
        "cc_max_methode_touchee": max((c["cc"] for x in m for c in x["methodes_touchees_cc"]
                                       if c["fichier"].startswith("src/main")), default=0),
        "pmd_nouveaux": sum(len(x["pmd_nouveaux"]) for x in m),
        "cpd_nouveaux": sum(len(x["cpd_nouveaux"]) for x in m),
        "spotbugs_nouveaux": sum(len(x["spotbugs_nouveaux"]) for x in m),
        "tests_ajoutes": len(tests),
        "assertions_par_test": moy(t["assertions"] for t in tests),
        "tests_sans_assertion": sum(1 for t in tests if t["assertions"] == 0 and not t["assertion_indirecte"]),
        "part_null_vide": round(sum(t["null_vide"] for t in tests) / len(tests), 2) if tests else None,
        "part_erreur": round(sum(t["erreur"] for t in tests) / len(tests), 2) if tests else None,
        "part_frontiere": round(sum(t["frontiere"] for t in tests) / len(tests), 2) if tests else None,
        "part_un_cas_limite": round(sum(t["null_vide"] or t["erreur"] or t["frontiere"] for t in tests) / len(tests), 2)
        if tests else None,
        "couverture_lignes_ajoutees": round(cov / exe, 3) if exe else None,
        "methodes_jamais_appelees": sum(len(x["methodes_jamais_appelees"]) for x in m),
        "methodes_test_seulement": sum(len(x["methodes_appelees_seulement_par_tests"]) for x in m),
        "types_jamais_references": sum(len(x["types_jamais_references"]) for x in m),
        "compile": sum(x["compile"] for x in m),
        "tests_verts": sum(x["tests"]["echecs"] + x["tests"]["erreurs"] == 0 for x in m),
    }


def main() -> None:
    mesures = charger(ICI / "mesures.jsonl")
    par = defaultdict(list)
    for x in mesures:
        par[x["etiquette"]].append(x)
    synth = {"mesures": {k: groupe_mesures(v) for k, v in sorted(par.items())}}

    passages = {}
    for etiq in ("sonnet-A", "sonnet-C", "opus-A"):
        p = charger(ICI / "passages" / f"{etiq}.jsonl")
        passages[etiq] = {"passages": len(p), "cout_total_usd": round(sum(x["agent"]["cout_usd"] or 0 for x in p), 3),
                          "cout_moyen_usd": moy(x["agent"]["cout_usd"] or 0 for x in p),
                          "duree_moyenne_s": moy(x["agent"]["duree_s"] for x in p),
                          "violations_nouvelles_11_regles": sum(x["violations_nouvelles_total"] for x in p),
                          "tests_verts": sum(x["tests_fonctionnels_ok"] for x in p)}
    synth["passages"] = passages

    revue = json.loads((ICI / "revue.json").read_text()) if (ICI / "revue.json").exists() else None
    if revue:
        rem = [r for c in revue["copies"] for r in c["remarques"]]
        cpt = defaultdict(int)
        for r in rem:
            cpt[r["vue_par"]] += 1
        synth["revue"] = {"remarques": len(rem), "par_classe": dict(cpt),
                          "couverture_harnais": round(cpt["regles"] / len(rem), 3) if rem else None,
                          "couverture_outils": round(cpt["outils"] / len(rem), 3) if rem else None,
                          "vues_par_personne": round(cpt["personne"] / len(rem), 3) if rem else None,
                          "avec_regle_voisine": sum(1 for r in rem if r["regle_voisine"]),
                          "par_categorie": {}}
        cat = defaultdict(lambda: defaultdict(int))
        for r in rem:
            cat[r["categorie"]][r["vue_par"]] += 1
        synth["revue"]["par_categorie"] = {k: dict(v) for k, v in sorted(cat.items())}

    d = charger(ICI / "defauts-resultats.jsonl")
    if d:
        synth["defauts"] = {"injectes": len(d),
                            "vus_par_regles": sum(x["vu_par_regles"] for x in d),
                            "vus_par_outils": sum(x["vu_par_outils"] for x in d),
                            "vus_par_tests": sum(x["vu_par_tests"] for x in d),
                            "vus_par_quelquun": sum(x["vu_par_quelquun"] for x in d),
                            "vus_par_personne": sum(not x["vu_par_quelquun"] for x in d),
                            "vus_par_outils_signal_pertinent": sum(x["outils_signal_pertinent"] for x in d),
                            "vus_par_quelquun_pertinent": sum(x["vu_par_quelquun_pertinent"] for x in d),
                            "avec_regle_voisine": sum(bool(x["regle_voisine"]) for x in d),
                            "avec_regle_voisine_vus_par_regles": sum(bool(x["regle_voisine"]) and x["vu_par_regles"] for x in d)}
    (ICI / "synthese.json").write_text(json.dumps(synth, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(synth, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
