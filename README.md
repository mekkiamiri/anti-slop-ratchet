# anti-slop-ratchet

**Mon agent ne fait plus d'AI slop. Mes règles servent à autre chose : lui faire rembourser la dette.**

Dépôt de démo du talk « Votre agent suit vos règles. Que laissent-elles passer ? » (Tools-in-Action, 30 min, proposé à Devoxx France 2027). J'avais changé 11 remarques de revue en 11 règles ArchUnit branchées dans la boucle de l'agent, pour l'empêcher de faire du slop. Mesuré sur 180 passages, l'agent ne fait pas ces erreurs, même sans règles ; les règles branchées, elles, lui font nettoyer la dette existante. Résultats complets : [mesures/README.md](mesures/README.md).

- Page du catalogue (filtrable, avec un essai en direct) : https://mekkiamiri.github.io/anti-slop-ratchet/
- Slides : https://mekkiamiri.github.io/anti-slop-ratchet/slides/
- La méthode, le prompt type et le branchement du hook : [RATCHET.md](RATCHET.md)
- Le banc de mesure (tickets, projet sale, compteur, données brutes) : [mesures/](mesures/)

## L'outil : harness-mutant

Mesurez la couverture de votre propre harnais en une commande : `harness-mutant` injecte des défauts
réalistes dans une copie de votre projet, lance votre harnais et compte ce qu'il attrape.

```bash
pip install ./outil
harness-mutant --projet . --commande "mvn -o -q verify"
# Votre harnais attrape 7 défauts sur 13 (54 %).  attrapés par : tests 7
# Les 6 trous : J13 contrôle de null retiré (Order.java:30) ...
```

Documentation, catalogue de défauts extensible et sorties réelles : [outil/README.md](outil/README.md).
Il s'appuie sur [PIT](https://pitest.org/), [ArchUnit](https://www.archunit.org/), [PMD](https://pmd.github.io/) et [SpotBugs](https://spotbugs.github.io/).

## Ce qui a été mesuré (22/11/2026, 180 passages, modèle servi : Sonnet 5.5)

| Projet | Condition | Nouvelles erreurs | Erreurs à la fin | Tests verts | Coût moyen | Durée |
|---|---|---|---|---|---|---|
| propre | A rien | 0 | 0 | 30/30 | 0,144 $ | 38 s |
| propre | B consignes (CLAUDE.md) | 0 | 0 | 30/30 | 0,140 $ | 37 s |
| propre | C règles + hook | 0 | 0 | 30/30 | 0,183 $ | 59 s |
| sale (11 erreurs au départ) | A rien | 0 | 11 | 30/30 | 0,163 $ | 46 s |
| sale | B consignes | 0 | 10,2 | 30/30 | 0,156 $ | 40 s |
| sale | C règles + hook | 0 | **0 (30 fois sur 30)** | 30/30 | 0,259 $ | 87 s |

Limites : un seul modèle, un petit projet (414 lignes), réussite = « compile et tests verts ».

## Ce qui tourne

- Un petit projet **Spring Boot 4.1.2 / Java 21** de gestion de commandes (`src/main/java/io/github/mekkiamiri/ratchet`) : domaine, cas d'usage, stockage en mémoire avec verrou optimiste (testé en concurrence), API REST validée (un JSON incomplet donne 400).
- **11 règles anti-slop** en ArchUnit 1.5.1 ([`AntiSlopRules.java`](src/test/java/io/github/mekkiamiri/ratchet/rules/AntiSlopRules.java)), chacune avec la remarque de revue d'origine dans son message d'échec.
- **11 mauvais / 11 bons exemples** (un dossier de chaque par règle) dans [`slopexamples`](src/test/java/io/github/mekkiamiri/slopexamples) (`rNN/bad` et `rNN/good`), hors du code de production et hors du scan Spring.
- **Les règles sont testées** ([`AntiSlopRulesTest`](src/test/java/io/github/mekkiamiri/ratchet/rules/AntiSlopRulesTest.java)) : chacune attrape chaque classe `*Slop` de son mauvais exemple et laisse passer le bon.
- **Les règles sont appliquées** au projet, toutes reprises automatiquement ([`ProjectArchTest`](src/test/java/io/github/mekkiamiri/ratchet/rules/ProjectArchTest.java), [`TestSourcesArchTest`](src/test/java/io/github/mekkiamiri/ratchet/rules/TestSourcesArchTest.java)), et [`ProjectLayoutArchTest`](src/test/java/io/github/mekkiamiri/ratchet/rules/ProjectLayoutArchTest.java) casse si un paquet visé par une règle disparaît.
- **Hook Claude Code** ([`.claude/settings.json`](.claude/settings.json), [`.claude/hooks/archunit-gate.sh`](.claude/hooks/archunit-gate.sh)) : après chaque fichier `.java` écrit par l'agent, et avant qu'il rende la main, `mvn -q test -Dtest='*ArchTest'` ; en cas d'échec, l'agent lit les violations.
- **CI** GitHub Actions : `mvn -B verify` sur Java 21.

## Lancer

```bash
mvn -B verify
```

Prérequis : Java 21 et Maven. Seulement les règles : `mvn -q test -Dtest='*ArchTest'`.

## État

| Élément | État |
|---|---|
| Projet Spring Boot public d'exemple | tourne, testé |
| 11 règles ArchUnit, 3 tests par règle + 1 test de cohérence du catalogue | tourne |
| Page de cohérence (chaque règle documentée sur la page et dans RATCHET.md) | tourne (`CatalogPageTest`) |
| Hook Claude Code `PostToolUse` + `Stop` | tourne : utilisé dans les 60 passages « règles + hook » de la mesure ; pas encore de session filmée |
| Mesure : l'agent avec ou sans règles, projet propre et projet sale | fait, 180 passages ([mesures/README.md](mesures/README.md)) |
| Mesure avec d'autres modèles, sur un gros projet | pas fait |
| Faux positifs des règles en revue réelle | pas mesuré |
| Revue croisée de 10 diffs (agent de revue + juge à l'aveugle) | fait le 28/11/2026 : 34 défauts, 0 vu par le harnais ([mesures/these-a/revue-croisee/](mesures/these-a/revue-croisee/README.md)) |
| Outil `harness-mutant` (Python, bibliothèque standard) | tourne, 16 tests en CI ([outil/](outil/README.md)) ; pas encore publié sur PyPI |
| Coût en temps de la commande du hook | 2,7 s sur ce projet après un fichier modifié (5 passages, 22/11/2026) ; gros module : pas mesuré |
| Règles sur le code source (Error Prone, Checkstyle) | pas fait |
| Adoption sur du code existant avec `FreezingArchRule` | décrite dans RATCHET.md, pas d'exemple dans ce dépôt |
| Vidéo de secours de la démo | pas faite |

Chaque chiffre publié ici vient des données brutes de `mesures/resultats/`.

## Sources

- Fabian Letsch, [Linters: The Most Underabused Tool In The AI-Slop Era](https://letsch.dev/blog/linters-the-most-underabused-tool-in-the-ai-slop-era/), avril 2026.
- Birgitta Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html), avril 2026 (guides et capteurs).
- [peteromallet/desloppify](https://github.com/peteromallet/desloppify) : une autre approche, un score global de qualité et une boucle de correction pour l'agent.
- [ArchUnit](https://www.archunit.org/), [doc des hooks Claude Code](https://code.claude.com/docs/en/hooks).

## Licence

Apache-2.0, voir [LICENSE](LICENSE).
