"""Tests de harness-mutant (bibliothèque standard : python3 -m unittest discover -s outil/tests)."""
from __future__ import annotations

import io
import json
import re
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness_mutant import cli  # noqa: E402
from harness_mutant.sonde import (  # noqa: E402
    Defaut, ajouter_imports, candidats, charger_catalogue, lignes_ajoutees, qui_a_sonne, sonder)

JAVA = textwrap.dedent("""\
    package demo;

    import java.math.BigDecimal;

    public class Prix {
        static final BigDecimal SEUIL = new BigDecimal("100");

        public static boolean remise(BigDecimal total) {
            if (total.compareTo(SEUIL) > 0) {
                return true;
            }
            return false;
        }

        public static BigDecimal net(BigDecimal total) {
            return total.multiply(new BigDecimal("0.9"));
        }
    }
    """)

# Un « harnais » en Python : vert tant que la frontière est stricte (simule un test à la valeur exacte).
HARNAIS = textwrap.dedent("""\
    import pathlib, sys
    src = pathlib.Path("src/main/java/demo/Prix.java").read_text()
    if "compareTo(SEUIL) >= 0" in src:
        print("Tests run: 3, Failures: 1, Errors: 0")
        sys.exit(1)
    sys.exit(0)
    """)


def projet_jouet(dossier: Path) -> Path:
    p = dossier / "jouet"
    (p / "src/main/java/demo").mkdir(parents=True)
    (p / "src/main/java/demo/Prix.java").write_text(JAVA)
    (p / "harnais.py").write_text(HARNAIS)
    return p


class CatalogueTest(unittest.TestCase):
    def test_le_catalogue_livre_se_charge_et_ses_motifs_compilent(self):
        defauts = charger_catalogue(None)
        self.assertGreaterEqual(len(defauts), 20)
        for d in defauts:
            self.assertTrue(d.pour_l_attraper, d.id)
            re.compile(d.chercher)

    def test_un_champ_inconnu_est_refuse(self):
        with self.assertRaises(ValueError):
            Defaut.depuis({"id": "X", "nom": "x", "famille": "f", "chercher": "a", "remplacer": "b", "typo": 1})

    def test_un_defaut_sans_motif_est_refuse(self):
        with self.assertRaises(ValueError):
            Defaut.depuis({"id": "X", "nom": "x", "famille": "f"})

    def test_les_identifiants_en_double_sont_refuses(self):
        with tempfile.TemporaryDirectory() as t:
            f = Path(t) / "c.json"
            d = {"id": "X", "nom": "x", "famille": "f", "chercher": "a", "remplacer": "b"}
            f.write_text(json.dumps({"defauts": [d, d]}))
            with self.assertRaises(ValueError):
                charger_catalogue([str(f)])


class InjectionTest(unittest.TestCase):
    def test_import_ajoute_apres_le_paquet_une_seule_fois(self):
        s = ajouter_imports(JAVA, ["java.time.Instant", "java.math.BigDecimal"])
        self.assertEqual(s.count("import java.time.Instant;"), 1)
        self.assertEqual(s.count("import java.math.BigDecimal;"), 1)
        self.assertLess(s.index("package demo;"), s.index("import java.time.Instant;"))

    def test_candidat_regex_donne_fichier_ligne_et_remplacement(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            j01 = next(d for d in charger_catalogue(None) if d.id == "J01")
            c = candidats(p, j01, [])
            self.assertEqual(len(c), 1)
            self.assertEqual((c[0].fichier, c[0].ligne), ("src/main/java/demo/Prix.java", 9))
            self.assertIn("compareTo(SEUIL) >= 0", c[0].fichiers[c[0].fichier])

    def test_exclusion_par_motif_de_chemin(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            j01 = next(d for d in charger_catalogue(None) if d.id == "J01")
            self.assertEqual(candidats(p, j01, ["*/demo/*"]), [])

    def test_forme_exacte_compatible_avec_le_banc(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            d = Defaut.depuis({"id": "D01", "nom": "seuil", "famille": "logique", "remplacements": [
                {"fichier": "src/main/java/demo/Prix.java", "avant": ") > 0)", "apres": ") >= 0)"}]})
            c = candidats(p, d, [])
            self.assertEqual(len(c), 1)
            self.assertIn(">= 0", c[0].fichiers["src/main/java/demo/Prix.java"])

    def test_lignes_ajoutees_d_un_diff_unifie(self):
        diff = textwrap.dedent("""\
            diff --git a/src/A.java b/src/A.java
            --- a/src/A.java
            +++ b/src/A.java
            @@ -8,2 +8,3 @@ class A {
                 int a;
            -    int b;
            +    int c;
            +    int d;
            --- /dev/null
            +++ b/src/B.java
            @@ -0,0 +1,2 @@
            +class B {
            +}
            """)
        self.assertEqual(lignes_ajoutees(diff), {"src/A.java": {9, 10}, "src/B.java": {1, 2}})

    def test_les_cibles_limitent_aux_lignes_de_l_agent(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            j01 = next(d for d in charger_catalogue(None) if d.id == "J01")
            self.assertEqual(len(candidats(p, j01, [], {"src/main/java/demo/Prix.java": {9}})), 1)
            self.assertEqual(candidats(p, j01, [], {"src/main/java/demo/Prix.java": {16}}), [])

    def test_signaux_reconnus_dans_la_sortie(self):
        self.assertEqual(qui_a_sonne("Rule 'R08 ...' was violated (1 times)\nThere are test failures"),
                         ["ArchUnit", "tests"])
        self.assertEqual(qui_a_sonne("[INFO] PMD Failure: Prix.java:9 Rule:CloseResource"), ["PMD"])
        self.assertEqual(qui_a_sonne("tout va bien"), [])


class SondeTest(unittest.TestCase):
    def test_bout_en_bout_un_attrape_un_trou_et_le_projet_n_est_pas_modifie(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            avant = (p / "src/main/java/demo/Prix.java").read_text()
            defauts = [d for d in charger_catalogue(None) if d.id in ("J01", "J04")]
            defauts.append(Defaut.depuis({"id": "X1", "nom": "retour inversé", "famille": "logique",
                                          "chercher": r"return false;", "remplacer": "return true;"}))
            s = sonder(p, f"{sys.executable} harnais.py", defauts, [], journal=lambda *_: None)
            statuts = {r["id"]: r["statut"] for r in s["resultats"]}
            self.assertEqual(statuts, {"J01": "attrape", "J04": "non_applicable", "X1": "trou"})
            self.assertEqual((s["attrapes"], s["comptes"], s["score"]), (1, 2, 50))
            self.assertEqual(s["par_signal"], {"tests": 1})
            self.assertEqual((p / "src/main/java/demo/Prix.java").read_text(), avant)

    def test_harnais_rouge_avant_injection(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            s = sonder(p, f"{sys.executable} -c 'raise SystemExit(3)'", charger_catalogue(None), [],
                       journal=lambda *_: None)
            self.assertIn("erreur", s)

    def test_un_defaut_qui_ne_compile_pas_n_est_pas_compte(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            d = Defaut.depuis({"id": "X2", "nom": "casse", "famille": "f",
                               "chercher": r"return true;", "remplacer": "return true"})
            harnais = f"{sys.executable} -c \"import pathlib,sys; s=pathlib.Path('src/main/java/demo/Prix.java').read_text(); sys.exit(print('COMPILATION ERROR') or 1 if 'return true\\n' in s else 0)\""
            s = sonder(p, harnais, [d], [], journal=lambda *_: None)
            self.assertEqual(s["ne_compilent_pas"], ["X2"])
            self.assertEqual(s["comptes"], 0)

    def test_reglages_du_projet_lus_dans_harness_mutant_json(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            (p / ".harness-mutant.json").write_text(json.dumps({"exclure": ["*/demo/*"]}))
            sortie = io.StringIO()
            with redirect_stdout(sortie):
                cli.main(["--projet", str(p), "--commande", "x", "--lister", "--seulement", "J01"])
            self.assertIn("non applicable", sortie.getvalue())

    def test_cli_rapport_et_seuil(self):
        with tempfile.TemporaryDirectory() as t:
            p = projet_jouet(Path(t))
            sortie = io.StringIO()
            with redirect_stdout(sortie):
                code = cli.main(["--projet", str(p), "--commande", f"{sys.executable} harnais.py",
                                 "--seulement", "J01,J03", "--silencieux", "--seuil", "100",
                                 "--json", str(Path(t) / "r.json")])
            texte = sortie.getvalue()
            self.assertIn("Votre harnais attrape 1 défaut sur 2 (50 %).", texte)
            self.assertIn("J03", texte)
            self.assertEqual(code, 1)
            self.assertEqual(json.loads((Path(t) / "r.json").read_text())["score"], 50)


if __name__ == "__main__":
    unittest.main()
