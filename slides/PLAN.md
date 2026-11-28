# Plan du deck v4 : « Votre agent suit vos règles. Que laissent-elles passer ? »

Tools-in-Action, 30 min, 15 slides (liste Quickie 20 min plus bas). Source : `slides/slides.html` → `docs/slides/index.html`.
Chaque slide appartient à une des 4 étapes, affichée en surtitre : **Départ → Problème → Cible → Comment**.

**Public :** développeurs Java, tech leads et architectes qui encadrent un agent de code avec des règles (tests, linters, ArchUnit, hooks), niveau intermédiaire.

**Ce qui change par rapport à la v3** (leçons de la relecture du talk voisin de la série) :
1. Aucun mot imagé ni jargon laissé sans explication : agent de code, harnais, linter (slide 2), ArchUnit (3), hook (4), mutation testing (6), revue croisée et juge à l'aveugle (7), trou (11), oracle, mutant, non applicable (12), PIT (13), diff vide (14). « Sonner » est remplacé par « échouer ». Le mot « slop » n'apparaît plus dans le texte des slides (seulement dans le nom du dépôt et dans la sortie réelle du hook, expliqué sur la capture).
2. Aucun contresens possible : le titre ne dit plus « aveugle ». Les règles, les tests et ArchUnit sont montrés utiles (0 contournement sur 144, dette nettoyée 30/30, linters et tests 7/20, tests 7/13, une règle ArchUnit ferme un trou) ; le message est « ils sont utiles, mais vous ne savez pas ce qu'ils attrapent : mesurez-le avec harness-mutant et fermez les trous ». Slide 1 : « Je ne vous dirai pas de les jeter » ; slide 10 : « Ce que ce talk ne dit pas ».
3. Six captures réelles (dossier `docs/slides/img/`, sources HTML et script dans `slides/captures/`, rendu WebKit headless) : règle ArchUnit et son message d'échec, hook qui renvoie l'agent corriger, revue croisée, diff de l'agent avec le défaut UTC surligné, sortie de harness-mutant avant et après le patch.

## Le chemin en 4 étapes

| Étape | En une phrase |
|---|---|
| **Départ** (ce que vous avez) | Votre agent de code est encadré par un harnais : règles ArchUnit, tests, linters, un hook qui le renvoie corriger. Ça marche : l'agent ne contourne pas les règles (0/144) et, sur 180 tâches ordinaires, aucune n'échoue. |
| **Problème** (ce qui fait mal) | Un harnais qui n'échoue jamais ne dit pas ce qu'il laisse passer. Mesuré : deux relecteurs trouvent 34 défauts dans 10 diffs de l'agent, ni règle, ni linter, ni test ne les signale ; sur 20 défauts injectés, 13 passent sans que rien n'échoue. |
| **Cible** (ce que vous voulez) | Ne pas jeter ses règles (slide 10) ; savoir ce que son harnais attrape, comme la couverture de ses tests : un score, la liste des trous, et la règle ou le test qui fermerait chacun. |
| **Comment** (l'outil + 3 gestes) | 1. Lancer `harness-mutant` sur son projet, fermer les trous, un score minimum en CI. 2. Autoriser l'agent à s'arrêter et expliquer (coût ÷ 2,2). 3. Refuser un résultat « 0 violation, tests verts » si le diff est vide. |

**L'outil :** `harness-mutant` (dossier `outil/`, Python bibliothèque standard, Apache-2.0).
`harness-mutant --projet . --commande "mvn -o -q verify"` → « Votre harnais attrape 7 défauts sur 13 (54 %) ; les 6 trous : … ». Reprend l'idée du mutation testing (PIT), et fait jouer ArchUnit, PMD, SpotBugs, les tests, Maven : tout ce que lance votre build.

**Objectif du talk (ce que le public fera lundi) :** lancer `harness-mutant` sur son projet, lire ses trous, et fermer le premier, sans rien retirer de son harnais.

**Promesse (« vous repartirez avec ») :**
1. La réponse mesurée à la question de Böckeler sur un vrai harnais : l'agent respecte les règles, et elles ne voient que ce qu'elles visent.
2. Un outil open source pour mesurer ce que votre harnais attrape en une commande, avec un catalogue de défauts extensible.
3. Deux garde-fous gratuits : l'agent autorisé à s'arrêter, le diff vide refusé.

**Le message en une phrase :** gardez vos règles, mesurez ce qu'elles attrapent, fermez les trous.

## Table par slide

| n° | étape | titre-phrase | capture | objectif : le public pense… | preuve | durée |
|---|---|---|---|---|---|---|
| 1 | Départ | Votre agent suit vos règles. Que laissent-elles passer ? | | « Il ne va pas me dire de tout jeter ; il y a un outil au bout. » | 0/144 ; 0/34 ; 7 → 10 sur 13 | 1 min 30 |
| 2 | Départ | Un agent de code écrit votre code seul ; son harnais, c'est tout ce qui vérifie ce qu'il écrit. | | « Je comprends les mots. » | définitions (Böckeler pour « harnais ») | 1 min 30 |
| 3 | Départ | Une règle ArchUnit transforme une remarque de revue en test qui échoue. | 01-regle-archunit | « C'est simple et utile. » | AntiSlopRules.java:71-76 ; message réel de mvn test | 2 min |
| 4 | Départ | Le hook renvoie l'agent corriger : il corrige le code, jamais la règle. | 02-hook-renvoie | « Les règles encadrent vraiment l'agent. » | contournement/README.md : 0/144, 144 citent la règle ; réponse réelle V2-I07 ; sortie du hook rejouée sur le même code | 2 min 30 |
| 5 | Départ | Mes règles servent, et pourtant, sur 180 tâches ordinaires, elles n'ont jamais échoué. | | « Silence, mais elles servent (dette 30/30). » | mesures/README.md : 180 passages, 0 violation, 180/180 verts, dette 30/30, +59 % | 1 min 30 |
| 6 | Problème | Un harnais qui n'échoue jamais ne dit pas ce qu'il laisse passer. | | « Je ne sais pas ce que mon harnais attrape. » | Böckeler, martinfowler.com, 02/04/2026 (traduit) | 1 min 30 |
| 7 | Problème | Deux relecteurs trouvent 34 défauts dans 10 diffs de l'agent ; ni règle, ni linter, ni test ne les signale. | 06-revue-croisee | « Mon harnais regarde ailleurs. » | revue-croisee/ : 31 + 21 constats, 34 défauts, 18 par les deux, 6 majeurs ; 0/34 règles, PMD/SpotBugs, tests | 2 min 30 |
| 8 | Problème | Du java.time propre, et une livraison annoncée un jour trop tôt. | 03-diff-order-utc | « Voilà un défaut d'agent en 2026. » | aveugle/diffs/sonnet-A-T03-A-1.diff ; REVIEW.md CR-04, WR-20 ; jugement.json diff K | 2 min |
| 9 | Problème | Sur 20 défauts injectés exprès, 13 passent sans que rien n'échoue. | | « Même mécaniquement. Mais linters et tests servent. » | aveugle/defauts-resultats.jsonl : 0 / 4 / 3 / 13 | 2 min |
| 10 | Cible | Ce talk ne dit pas « jetez vos règles ». Il dit : mesurez ce qu'elles attrapent. | | « Je garde tout, je mesure. » | rappel 0/144, 30/30, tests 7/13 | 1 min 30 |
| 11 | Cible | Savoir ce que votre harnais attrape, comme la couverture de vos tests. | | « C'est ça que je veux. » | (la cible) | 1 min |
| 12 | Comment | harness-mutant casse une copie de votre projet, un défaut à la fois, et compte ce que votre harnais attrape. | 04-harness-mutant-avant | « Une commande, je peux le faire lundi. » | outil/exemples/sortie-projet-du-talk.txt : 7/13 ; démo live | 3 min 30 |
| 13 | Comment | Une règle et deux tests : le score passe de 7 à 10 sur 13. | 05-harness-mutant-apres | « Chaque trou se ferme ; une règle ArchUnit en ferme un. » | fermer-les-trous.patch, sortie-apres-patch.txt | 2 min 30 |
| 14 | Comment | Mesurez votre harnais, autorisez l'agent à s'arrêter, ne validez pas un diff vide. | | « Trois gestes, dont un outil. » | ÷ 2,2 (V3, 48/48) ; 15 passages vides comptés réussis | 2 min |
| 15 | Comment | Gardez vos règles. Mesurez ce qu'elles attrapent. Fermez les trous. | | La phrase à retenir, et la commande à taper. | dépôt public, limites | 2 min |

Total : 30 min. Le résultat « 3 défauts sur 40 dans les lignes de l'agent » (`--diff`, revue-croisee/harnais-lignes-agent/) n'a plus de slide : il est dit dans les notes si le temps le permet.

## Quickie 20 min (10 slides)

1, 2, 3, 4, 7, 8, 10, 12, 13, 15 : on garde le chemin, les définitions, les captures et la démo ; on retire les 180 tâches (une phrase sur la 4), la citation (une phrase sur la 7), l'injection du banc (9, remplacée par la démo), la cible (dite sur la 10) et les trois gestes (le premier est dit sur la 15).

## Skim test (titres lus seuls)

Votre agent suit vos règles. Que laissent-elles passer ? Un agent de code écrit votre code seul ; son harnais, c'est tout ce qui vérifie ce qu'il écrit. Une règle ArchUnit transforme une remarque de revue en test qui échoue. Le hook renvoie l'agent corriger : il corrige le code, jamais la règle. Mes règles servent, et pourtant, sur 180 tâches ordinaires, elles n'ont jamais échoué. Un harnais qui n'échoue jamais ne dit pas ce qu'il laisse passer. Deux relecteurs trouvent 34 défauts dans 10 diffs de l'agent ; ni règle, ni linter, ni test ne les signale, comme ce java.time propre qui annonce une livraison un jour trop tôt ; sur 20 défauts injectés exprès, 13 passent sans que rien n'échoue. Ce talk ne dit pas « jetez vos règles », il dit : mesurez ce qu'elles attrapent, comme la couverture de vos tests. harness-mutant casse une copie de votre projet, un défaut à la fois, et compte ce que votre harnais attrape ; une règle et deux tests font passer le score de 7 à 10 sur 13. Mesurez votre harnais, autorisez l'agent à s'arrêter, ne validez pas un diff vide. Gardez vos règles, mesurez ce qu'elles attrapent, fermez les trous.

## Captures

| Fichier (`docs/slides/img/`) | Slide | Ce qu'elle montre | Source |
|---|---|---|---|
| 01-regle-archunit.png | 3 | la règle R03 et son message d'échec dans `mvn test` | AntiSlopRules.java:71-76 ; sortie Maven réelle (OrderService avec `Optional.get()`, copie jetable) |
| 02-hook-renvoie.png | 4 | la sortie du hook Stop (« Corrige le code, pas la règle ») puis la réponse de l'agent qui remet le code conforme | `.claude/hooks/archunit-gate.sh` lancé sur le même code (les retours du hook ne sont pas gardés dans la transcription) ; réponse : contournement/brut/V2, ticket I07, coupes […] |
| 06-revue-croisee.png | 7 | les deux relecteurs sur le défaut UTC, et le croisement 0/34 | agent-de-revue/REVIEW.md (CR-04, WR-20), juge-aveugle/jugement.json (diff K), croisement.json |
| 03-diff-order-utc.png | 8 | le diff de l'agent, `ZoneOffset.UTC` et la date de test surlignés | aveugle/diffs/sonnet-A-T03-A-1.diff |
| 04-harness-mutant-avant.png | 12 | la sortie de harness-mutant : 7/13, les 6 trous et comment les fermer | outil/exemples/sortie-projet-du-talk.txt |
| 05-harness-mutant-apres.png | 13 | la sortie après le patch : 10/13, 3 trous (tests affaiblis) | outil/exemples/sortie-apres-patch.txt |

Refaire les captures : `slides/captures/capturer.sh` (WebKit headless via Playwright, sans fenêtre ; jamais le headless de Chrome). Aperçus du deck construit : `slides/apercu/`.

## Sources des chiffres

- `mesures/README.md` : 180 passages (10 tickets × 3 conditions × 3 essais × 2 projets), 0 violation ajoutée, 180/180 tests verts, dette nettoyée 30/30, +59 % de coût.
- `mesures/these-a/contournement/` : 144 passages, 0 contournement, 1 tentative bloquée, 144 réponses citent la règle, 18 décisions rendues, V3 48/48, coût ÷ 2,2.
- `mesures/these-a/revue-croisee/` (28/11/2026) : agent de revue 31 constats, juge à l'aveugle 21, 34 défauts uniques dont 18 trouvés par les deux et 6 majeurs ; vus par les 11 règles 0, par PMD/SpotBugs 0, par les tests 0 (témoins verts) ; harness-mutant sur les lignes de l'agent : 40 défauts, 0 attrapé par les règles, 3 par les tests, 37 trous.
- `mesures/these-a/aveugle/` (25/11/2026) : 20 défauts injectés (0 règles, 4 linters, 3 tests, 13 personne), 15 passages invalides (diff vide).
- `outil/exemples/` : sorties réelles de harness-mutant (7/13 avant, 10/13 après le patch ; harnais = `mvn -o -q verify`, règles + tests, sans linter).
- Böckeler, « Harness engineering for coding agent users », martinfowler.com, 02/04/2026 ; ImpossibleBench, arXiv 2510.20270.
