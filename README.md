# anti-slop-ratchet

**Chaque remarque de revue qui revient sur du code écrit par un agent devient une règle ArchUnit testée, branchée dans la boucle de l'agent et dans la CI.**

Dépôt de démo du talk « Contre l'AI slop : un linter Java qui apprend des revues » (Tools-in-Action, 30 min, proposé à Devoxx France 2027).

- Page du catalogue (filtrable, avec un essai en direct) : https://mekkiamiri.github.io/anti-slop-ratchet/
- Slides : https://mekkiamiri.github.io/anti-slop-ratchet/slides/
- La méthode, le prompt type et le branchement du hook : [RATCHET.md](RATCHET.md)

## Ce qui tourne

- Un petit projet **Spring Boot 4.1.2 / Java 21** de gestion de commandes (`src/main/java/io/github/mekkiamiri/ratchet`) : domaine, cas d'usage, stockage en mémoire, API REST.
- **11 règles anti-slop** en ArchUnit 1.5.1 ([`AntiSlopRules.java`](src/test/java/io/github/mekkiamiri/ratchet/rules/AntiSlopRules.java)), chacune avec la remarque de revue d'origine dans son message d'échec.
- **22 exemples volontairement fautifs ou corrigés** dans [`slopexamples`](src/test/java/io/github/mekkiamiri/slopexamples) (`rNN/bad` et `rNN/good`), hors du code de production et hors du scan Spring.
- **Les règles sont testées** ([`AntiSlopRulesTest`](src/test/java/io/github/mekkiamiri/ratchet/rules/AntiSlopRulesTest.java)) : chacune attrape chaque classe `*Slop` de son mauvais exemple et laisse passer le bon.
- **Les règles sont appliquées** au projet ([`ProjectArchTest`](src/test/java/io/github/mekkiamiri/ratchet/rules/ProjectArchTest.java), [`TestSourcesArchTest`](src/test/java/io/github/mekkiamiri/ratchet/rules/TestSourcesArchTest.java)).
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
| Projet Spring Boot d'exemple | tourne, testé |
| 11 règles ArchUnit + 33 tests des règles | tourne |
| Page de cohérence (chaque règle documentée sur la page et dans RATCHET.md) | tourne (`CatalogPageTest`) |
| Hook Claude Code `PostToolUse` + `Stop` | écrit, essayé à la main avec des entrées simulées ; pas encore en session réelle filmée |
| Remarques de revue avant / après | **à mesurer** (protocole dans RATCHET.md) |
| Faux positifs sur un vrai projet, coût en temps du hook | **à mesurer** |
| Règles sur le code source (Error Prone, Checkstyle) | pas fait |
| Vidéo de secours de la démo | pas faite |

Aucun chiffre de résultat n'est publié tant qu'il n'est pas mesuré.

## Sources

- Fabian Letsch, [Linters: The Most Underabused Tool In The AI-Slop Era](https://letsch.dev/blog/linters-the-most-underabused-tool-in-the-ai-slop-era/), avril 2026.
- Birgitta Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html), avril 2026 (guides et capteurs).
- [peteromallet/desloppify](https://github.com/peteromallet/desloppify) : une autre approche, un score global de qualité et une boucle de correction pour l'agent.
- [ArchUnit](https://www.archunit.org/), [doc des hooks Claude Code](https://code.claude.com/docs/en/hooks).

## Licence

Apache-2.0, voir [LICENSE](LICENSE).
