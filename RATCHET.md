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
Ajoute la ligne dans AntiSlopRulesTest.rules() et le champ @ArchTest dans ProjectArchTest.
Lance `mvn -q test -Dtest='AntiSlopRulesTest,*ArchTest'`. Ne modifie pas le code de production
pour faire passer la règle sans me montrer les violations trouvées.
```

### 3. Tester la règle elle-même

Une règle qui ne casse jamais ne protège de rien ; une règle qui casse sur du bon code sera désactivée au bout d'une semaine. `AntiSlopRulesTest` vérifie pour chaque règle :

- qu'elle signale **chaque** classe `*Slop` du dossier `bad` ;
- qu'elle ne signale **rien** dans le dossier `good` ;
- que sa description commence par son identifiant et cite la remarque de revue.

Exemple de faux positif évité : R01 interdit `catch (Exception)` et `catch (RuntimeException)`, mais pas `catch (Throwable)`, parce que javac compile chaque *try-with-resources* en `catch (Throwable)`. Le bon exemple `r01/good/PaymentGateway` utilise un try-with-resources pour le prouver.

### 4. Brancher la règle dans la boucle de l'agent et dans la CI

**Dans la boucle de l'agent** (le plus tôt possible, là où l'erreur naît) : `.claude/settings.json` branche [`.claude/hooks/archunit-gate.sh`](.claude/hooks/archunit-gate.sh) sur deux événements Claude Code (format vérifié sur la [doc officielle des hooks](https://code.claude.com/docs/en/hooks)) :

| Événement | Quand | Effet d'un `exit 2` |
|---|---|---|
| `PostToolUse`, matcher `Edit\|Write` | après chaque fichier `.java` écrit ou modifié | Claude lit les violations (stderr) et corrige tout de suite |
| `Stop` | quand l'agent veut rendre la main | Claude ne peut pas s'arrêter tant que les règles cassent |

```json
{
  "hooks": {
    "PostToolUse": [
      { "matcher": "Edit|Write",
        "hooks": [ { "type": "command", "command": "\"${CLAUDE_PROJECT_DIR}\"/.claude/hooks/archunit-gate.sh" } ] }
    ],
    "Stop": [
      { "hooks": [ { "type": "command", "command": "\"${CLAUDE_PROJECT_DIR}\"/.claude/hooks/archunit-gate.sh" } ] }
    ]
  }
}
```

Le script lit le JSON reçu sur l'entrée standard (`tool_input.file_path`, `stop_hook_active`), ne fait rien si le fichier n'est pas du Java, puis lance :

```bash
mvn -q -B test -Dtest='*ArchTest' -Dsurefire.failIfNoSpecifiedTests=false
```

Précision honnête : ArchUnit analyse les classes compilées, donc la commande vérifie tout le module, pas seulement le fichier modifié. Elle ne se *déclenche* que sur les fichiers Java modifiés. Sur ce petit projet, c'est rapide ; sur un gros module, le temps reste [à mesurer](#ce-qui-reste-à-mesurer).

Le hook `Stop` vérifie `stop_hook_active` pour ne pas relancer l'agent en boucle (Claude Code plafonne de toute façon à 8 relances consécutives, d'après la doc).

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
| R06 | `@Transactional` sur une méthode privée | méthode `@Transactional` ni privée ni finale |
| R07 | le contrôleur appelle le repository | `..web..` ne dépend pas de `*Repository` ni de `..infrastructure..` |
| R08 | `new BigDecimal(0.9)` pour de l'argent | pas d'appel au constructeur `BigDecimal(double)` |
| R09 | `Date` et `SimpleDateFormat` | `GeneralCodingRules.OLD_DATE_AND_TIME_CLASSES_SHOULD_NOT_BE_USED` |
| R10 | `throw new RuntimeException("error")` | `GeneralCodingRules.NO_CLASSES_SHOULD_THROW_GENERIC_EXCEPTIONS` |
| R11 | classe de test jamais lancée par Surefire | une méthode `@Test` vit dans une classe `*Test` |

Le détail (texte de la remarque, mauvais code, bon code) est dans [`AntiSlopRules.java`](src/test/java/io/github/mekkiamiri/ratchet/rules/AntiSlopRules.java), dans [`slopexamples`](src/test/java/io/github/mekkiamiri/slopexamples) et sur la [page du catalogue](https://mekkiamiri.github.io/anti-slop-ratchet/).

## Limites connues des règles

- **R01** ne voit pas le corps du `catch` (ArchUnit lit le bytecode, pas la source) : elle interdit tout `catch (Exception)`, même s'il relance proprement. C'est voulu : attraper l'exception précise est toujours possible.
- **R03** signale aussi un `get()` précédé de `isPresent()`. C'est voulu : `orElseThrow` dit la même chose sans le test.
- **R07** se fie au nom `*Repository` et au paquet `infrastructure` : adaptez-les à votre convention.
- **R11** exige le suffixe `Test`, plus strict que Surefire (qui lance aussi `Test*`, `*Tests`, `*TestCase`).

## Ce qui reste à mesurer

Le talk promet de **compter** les remarques de revue avant et après. Rien n'est encore mesuré. Protocole prévu :

1. Une même liste de tâches (ajouter une fonctionnalité au projet de commandes), confiée à un agent **sans** les règles puis **avec** les règles branchées dans le hook.
2. Pour chaque PR produite : nombre de remarques de revue relevant d'une règle du catalogue, nombre de remarques hors catalogue, faux positifs des règles, temps ajouté par le hook.
3. Publication des chiffres bruts dans `mesures/` (dossier à créer), avec les PR.

Tant que ces chiffres n'existent pas, la page et les slides affichent « à mesurer ».

## Pistes (pas encore faites)

- Règles sur le code source plutôt que le bytecode (Error Prone, Checkstyle, PMD) pour ce qu'ArchUnit ne voit pas : le corps des `catch`, les commentaires, les noms locaux.
- Gel des violations existantes (`FreezingArchRule` d'ArchUnit) pour adopter le ratchet sur un projet existant sans tout corriger d'un coup.
