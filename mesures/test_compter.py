import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compter import violations_depuis_texte  # noqa: E402

MESSAGE = """Architecture Violation [Priority: MEDIUM] - Rule 'R08 pas de new BigDecimal(double), avec ou sans MathContext, because revue : « new BigDecimal(0.1) vaut ... »' was violated (2 times):
Method <a.B.c()> calls constructor <java.math.BigDecimal.<init>(double)> in (B.java:5)
Architecture Violation [Priority: MEDIUM] - Rule 'R04 pas de System.out, System.err ni printStackTrace()' was violated (1 times):
Method <a.B.c()> gets field <java.lang.System.out> in (B.java:5)"""


class TestCompter(unittest.TestCase):
    def test_compte_par_regle(self):
        self.assertEqual(violations_depuis_texte(MESSAGE), {"R08": 2, "R04": 1})

    def test_rien(self):
        self.assertEqual(violations_depuis_texte("BUILD SUCCESS"), {})

    def test_additionne_les_occurrences(self):
        self.assertEqual(violations_depuis_texte(MESSAGE + "\n" + MESSAGE), {"R08": 4, "R04": 2})


if __name__ == "__main__":
    unittest.main()
