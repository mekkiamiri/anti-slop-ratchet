# Le ratchet anti-slop

Un cliquet (*ratchet*) ne tourne que dans un sens. Ici : chaque remarque de revue qui revient devient une règle, et une règle ajoutée ne s'enlève pas sans discussion. Le niveau du code ne peut que monter.

> « If you can describe a problem precisely, you can probably enforce it with a linter. »
> Fabian Letsch, [Linters: The Most Underabused Tool In The AI-Slop Era](https://letsch.dev/blog/linters-the-most-underabused-tool-in-the-ai-slop-era/) (avril 2026)

Pourquoi une règle plutôt qu'une ligne de plus dans le prompt : le prompt est un **guide** (il oriente l'agent *avant* qu'il agisse), la règle est un **capteur** (*sensor* : elle observe *après* et permet à l'agent de se corriger). Vocabulaire de Birgitta Böckeler, [Harness engineering for coding agent users](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) (avril 2026). Un guide peut être ignoré ; un capteur déterministe casse à chaque fois.

## La boucle en 4 étapes

```
remarque de revue récurrente ──► règle écrite par l'agent ──► testée (mauvais / bon) ──► branchée (hook agent + CI)
          ▲                                                                                        │
          └──────────────────────── la remarque ne revient plus en revue ◄─────────────────────────┘
```

### 1. Repérer la remarque qui revient

Critère simple : **la même remarque deux fois**, sur deux PR différentes (humaine ou agent). Notez-la telle quelle, avec un exemple de code fautif. Pas de règle pour une remarque unique : une règle a un coût (faux positifs, temps de build).

La remarque doit être **décidable sur le code compilé** : « pas de `new BigDecimal(double)` » l'est ; « ce nom de méthode est flou » ne l'est pas (gardez-la pour la revue humaine ou une revue par IA).

### 2. Faire écrire la règle par l'agent

Une règle ArchUnit est isolée du reste du code : c'est une tâche idéale pour un agent. Prompt type :

```text
Une remarque revient en revue de code :
« <remarque telle qu'écrite en revue> »

Exemple de code fautif :
<extrait>

Écris une règle ArchUnit dans src/test/java/io/github/mekkiamiri/ratchet/rules/AntiSlopRules.java :
- nom de constante R<NN>_<NOM>, description `.as("R<NN> <phrase courte>")` ;
- `.because("revue : « <la remarque d'origine> »")` : le message d'échec doit dire quoi faire à la place ;
- `.allowEmptyShould(true)` si la règle commence par `that()`.
Ajoute deux exemples dans src/test/java/io/github/mekkiamiri/slopexamples/r<NN>/ :
- bad/<Nom>Slop.java : le code fautif, minimal ;
- good/<Nom>.java : la correction attendue (pense au cas limite qui pourrait donner un faux positif).
Annote la constante avec @ArchTest (ProjectArchTest reprend automatiquement toutes les règles
de AntiSlopRules) et ajoute la ligne dans AntiSlopRulesTest.rules().
Lance `mvn -q test -Dtest='AntiSlopRulesTest,*ArchTest'`. Ne modifie pas le code de production
pour faire passer la règle sans me montrer les violations trouvées.
```

### 3. Tester la règle elle-même

Une règle qui ne casse jamais ne protège de rien ; une règle qui casse sur du bon code sera désactivée au bout d'une semaine. `AntiSlopRulesTest` vérifie pour chaque règle :

- qu'elle signale **chaque** classe `*Slop` du dossier `bad` ;
- qu'elle ne signale **rien** dans le dossier `good` ;
- que sa description commence par son identifiant et cite la remarque de revue ;
- et, pour tout le catalogue, qu'aucune règle de `AntiSlopRules` n'a été oubliée dans `AntiSlopRulesTest` (`ProjectArchTest` les reprend toutes via `ArchTests.in(AntiSlopRules.class)`).

Exemple de faux positif évité : R01 interdit `catch (Exception)` et `catch (RuntimeException)`, mais pas `catch (Throwable)`, parce que javac compile chaque *try-with-resources* en `catch (Throwable)`. Le bon exemple `r01/good/PaymentGateway` utilise un try-with-resources pour le prouver. Le prix : **un vrai `catch (Throwable t)` écrit à la main passe la règle. C'est un faux négatif assumé** (voir les limites plus bas).

### 4. Brancher la règle dans la boucle de l'agent et dans la CI

**Dans la boucle de l'agent** (le plus tôt possible, là où l'erreur naît) : `.claude/settings.json` branche [`.claude/hooks/archunit-gate.sh`](.claude/hooks/archunit-gate.sh) sur deux événements Claude Code (format vérifié sur la [doc officielle des hooks](https://code.claude.com/docs/en/hooks)) :

| Événement | Quand | Effet d'un `exit 2` |
|---|---|---|
| `PostToolUse`, matcher `Edit\|Write` | après un fichier `.java` écrit ou modifié | Claude lit les violations (stderr) et corrige tout de suite |
| `Stop` | quand l'agent veut rendre la main | Claude ne peut pas s'arrêter tant que les règles cassent |

Le matcher ne contient pas `MultiEdit` : la doc officielle des hooks ne cite pas d'outil de ce nom (vérifié le 16/11/2026), seulement `Edit|Write` dans ses exemples. Chaque hook a `"timeout": 180` (secondes ; 600 par défaut d'après la doc).

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "\"${CLAUDE_PROJECT_DIR}\"/.claude/hooks/archunit-gate.sh", "timeout": 180 } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "\"${CLAUDE_PROJECT_DIR}\"/.claude/hooks/archunit-gate.sh", "timeout": 180 } ] }
    ]
  }
}
```

Le script lit le JSON reçu sur l'entrée standard (`tool_input.file_path`), ne fait rien si le fichier n'est pas du Java, ni si les fichiers Java n'ont pas changé depuis le dernier passage réussi (empreinte de `git diff`, gardée dans `.git/archunit-gate.ok`), puis lance :

```bash
mvn -q -B test -Dtest='*ArchTest' -Dsurefire.failIfNoSpecifiedTests=false
```

Il distingue deux échecs :

- **violation ArchUnit** : `exit 2` avec les violations dédoublonnées ; le message de chaque règle contient la remarque de revue ;
- **build cassé** (compilation, dépendance absente, autre test) : `exit 2` avec « Build cassé, pas une règle anti-slop » et la sortie Maven tronquée, pour que l'agent ne cherche pas une règle qui n'existe pas.

Si `mvn`, `python3` ou `git` manque, le script sort en `exit 0` avec « gate anti-slop ignoré : mvn absent » : il ne bloque pas l'agent avec une fausse consigne.

Précision honnête : ArchUnit analyse les classes compilées, donc la commande vérifie tout le module, pas seulement le fichier modifié. Sur ce petit projet (61 fichiers Java), la commande Maven du hook prend 2,7 s après la modification d'un fichier (de 2,70 à 2,78 s sur 5 passages, le 22/11/2026, Apple M4 Pro, Java 25, Maven 3.10 hors ligne) ; sur un gros module, le temps sera publié avec les [autres mesures](#ce-qui-reste-à-mesurer). Pendant un refactor sur plusieurs fichiers, les étapes intermédiaires peuvent casser : `ARCH_GATE_ON_STOP_ONLY=1` ne vérifie qu'au `Stop`.

Au `Stop`, le script revérifie à chaque fois, même quand `stop_hook_active` est vrai : l'agent ne peut pas rendre la main avec une violation. Claude Code plafonne lui-même les relances (8 relances consécutives d'après la doc), puis laisse l'agent s'arrêter : à ce moment, c'est la CI qui bloque.

**Dans la CI** (le filet de sécurité) : `.github/workflows/ci.yml` lance `mvn -B verify`. Toutes les règles et leurs tests tournent dans la phase `test`.

Letsch déconseille les hooks git pre-commit et pre-push (ils ralentissent les commits fréquents) ; ici le contrôle se fait dans la boucle de l'agent et en CI.

## Le catalogue actuel

| Id | Remarque de revue (résumé) | Règle |
|---|---|---|
| R01 | `catch (Exception e)` qui avale l'erreur | pas de `catch (Exception)` ni `catch (RuntimeException)` |
| R02 | `@Autowired` sur un champ | `GeneralCodingRules.NO_CLASSES_SHOULD_USE_FIELD_INJECTION` |
| R03 | `Optional.get()` sans test | pas d'appel à `Optional.get()` (utiliser `orElseThrow`) |
| R04 | `System.out`, `printStackTrace()` | `GeneralCodingRules.NO_CLASSES_SHOULD_ACCESS_STANDARD_STREAMS` |
| R05 | `ResponseStatusException` levée par le service | `..domain..` et `..application..` ne dépendent pas du web ni de HTTP |
| R06 | `@Transactional` sur une méthode privée | méthode `@Transactional` (Spring ou Jakarta) ni privée ni finale |
| R07 | le contrôleur appelle le repository | `..web..` ne dépend pas de `*Repository` ni de `..infrastructure..` |
| R08 | `new BigDecimal(0.9)` pour de l'argent | pas d'appel à `BigDecimal(double)` ni `BigDecimal(double, MathContext)` |
| R09 | `Date` et `SimpleDateFormat` | `GeneralCodingRules.OLD_DATE_AND_TIME_CLASSES_SHOULD_NOT_BE_USED` |
| R10 | `throw new RuntimeException("error")` | `GeneralCodingRules.NO_CLASSES_SHOULD_THROW_GENERIC_EXCEPTIONS` |
| R11 | classe de test jamais lancée par Surefire | une méthode `@Test` vit dans une classe `Test*`, `*Test`, `*Tests` ou `*TestCase` (ou une classe `@Nested` d'une telle classe) |

Le détail (texte de la remarque, mauvais code, bon code) est dans [`AntiSlopRules.java`](src/test/java/io/github/mekkiamiri/ratchet/rules/AntiSlopRules.java), dans [`slopexamples`](src/test/java/io/github/mekkiamiri/slopexamples) et sur la [page du catalogue](https://mekkiamiri.github.io/anti-slop-ratchet/).

## Limites connues des règles

- **R01** ne voit pas le corps du `catch` (ArchUnit lit le bytecode, pas la source) : elle interdit tout `catch (Exception)`, même s'il relance proprement. C'est voulu : attraper l'exception précise est toujours possible.
- **R01, faux négatif assumé** : `catch (Throwable t)` n'est pas signalé, parce que javac compile chaque try-with-resources en `catch (Throwable)` et qu'ArchUnit ne distingue pas les deux. Les signaler tous rendrait la règle inutilisable.
- **R03** signale aussi un `get()` précédé de `isPresent()`. C'est voulu : `orElseThrow` dit la même chose sans le test.
- **R07** se fie au nom `*Repository` et au paquet `infrastructure` : adaptez-les à votre convention.
- **R06** reconnaît les annotations par leur nom (`org.springframework.transaction.annotation.Transactional`, `jakarta.transaction.Transactional`) : elle marche sans que Jakarta soit sur le classpath. Le projet d'exemple n'a pas de `@Transactional` (stockage en mémoire, sans gestionnaire de transactions : l'annotation n'y ferait rien) ; R06 est prouvée sur ses exemples.
- **R05 et R07** ont `allowEmptyShould(true)` : renommer un paquet les ferait passer en silence. `ProjectLayoutArchTest` casse si `..domain..`, `..application..`, `..web..`, `..infrastructure..` ou les classes `*Repository` disparaissent.
- **R11** suit les motifs par défaut de Surefire (`Test*`, `*Test`, `*Tests`, `*TestCase`) ; si votre `pom.xml` change les `<includes>`, changez la règle.

## Adopter les règles sur du code existant : `FreezingArchRule`

Sur un projet existant, une nouvelle règle trouve souvent des dizaines de violations. Les corriger toutes avant de brancher la règle, c'est la garantie qu'elle ne sera jamais branchée. ArchUnit fournit le cliquet tout fait : [`FreezingArchRule`](https://www.archunit.org/userguide/html/000_Index.html) (dans `com.tngtech.archunit.library.freeze`).

```java
@ArchTest
static final ArchRule r08 = FreezingArchRule.freeze(AntiSlopRules.R08_NO_BIGDECIMAL_FROM_DOUBLE);
```

D'après le guide ArchUnit :

- au premier passage, toutes les violations existantes sont enregistrées dans un magasin en fichiers texte, à versionner avec le code (`freeze.store.default.path` dans `archunit.properties`, et `freeze.store.default.allowStoreCreation=true` pour autoriser sa création) ;
- ensuite, **seules les nouvelles violations cassent le build** ; l'agent ne peut plus en ajouter ;
- quand une violation est corrigée, elle est retirée du magasin automatiquement : elle ne peut pas revenir.

C'est exactement le ratchet : le stock de dette ne peut que baisser. Ce dépôt n'en a pas besoin (son code respecte toutes les règles), donc il n'y a pas encore de magasin d'exemple.

## Ce qui a été mesuré

L'idée de départ était : « un prompt se suggère, une règle s'impose » ; les règles empêchent l'agent de faire du slop. Mesuré le 22/11/2026 sur 180 passages (10 tickets ordinaires, 3 conditions : rien, consignes écrites dans `CLAUDE.md`, règles + hook ; 2 projets : propre et sale ; 3 passages ; modèle servi : Sonnet 5.5), **cette idée est réfutée sur ce banc** :

1. l'agent n'ajoute **aucune** des 11 erreurs du catalogue, même sans règles ni consignes, même sur un projet qui en contient déjà 11 ;
2. les consignes écrites ne font presque rien nettoyer (11 → 10,2 erreurs en moyenne) ;
3. les règles branchées dans le hook font nettoyer **toute** la dette existante, 30 fois sur 30, tests verts, pour +59 % de coût et ×1,9 de temps.

Les règles ne servent donc pas ici de garde-fou contre l'agent, mais de levier pour rembourser la dette. Sur un vrai legacy, c'est le choix « geler ou rembourser » (`FreezingArchRule` ci-dessus).

Protocole, tableau complet, contrôles et limites (un seul modèle, petit projet, réussite = compile et tests verts) : [mesures/README.md](mesures/README.md). Pas encore mesuré : les remarques de revue humaine avant / après sur de vraies PR, les faux positifs des règles en revue réelle, d'autres modèles, un gros projet.

## Pistes (pas encore faites)

- Règles sur le code source plutôt que le bytecode (Error Prone, Checkstyle, PMD) pour ce qu'ArchUnit ne voit pas : le corps des `catch`, les commentaires, les noms locaux.
- Un exemple complet de `FreezingArchRule` sur un projet open source existant, avec son magasin de violations.
