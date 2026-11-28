# Plan du deck v3 : « Mon harnais était aveugle, pas mon agent »

Tools-in-Action, 30 min, 14 slides (liste Quickie 20 min plus bas). Source : `slides/slides.html` → `docs/slides/index.html`.
Chaque slide appartient à une des 4 étapes, affichée en surtitre : **Départ → Problème → Cible → Comment**.

**Public :** développeurs Java, tech leads et architectes qui encadrent un agent de code avec des règles (tests, linters, ArchUnit, hooks), niveau intermédiaire.

## Le chemin en 4 étapes

| Étape | En une phrase |
|---|---|
| **Départ** (ce que vous avez) | Vous avez mis votre agent de code dans un harnais : tests, linters, règles ArchUnit, un hook qui le bloque tant que c'est rouge. Les règles ne sonnent jamais (180 tâches, 0 violation). |
| **Problème** (ce qui fait mal) | Un harnais muet ne dit pas s'il protège. Mesuré : l'agent ne triche pas (0 contournement sur 144), mais deux relecteurs trouvent 34 défauts dans 10 de ses diffs et le harnais n'en voit aucun ; sur 20 défauts injectés, les règles en attrapent 0. Le harnais rassure, il ne protège pas. |
| **Cible** (ce que vous voulez) | Connaître la couverture de votre harnais comme celle de vos tests : un score, la liste des trous, et la règle ou le test qui fermerait chacun. |
| **Comment** (l'outil + 3 gestes) | 1. Lancer `harness-mutant` sur votre projet (il injecte des défauts réalistes et compte ce qui sonne), fermer les trous, mettre un seuil en CI. 2. Donner à l'agent le droit d'abandonner (coût ÷ 2,2). 3. Refuser un résultat « 0 violation, tests verts » si le diff est vide. |

**L'outil :** `harness-mutant` (dossier `outil/`, Python bibliothèque standard, Apache-2.0).
`harness-mutant --projet . --commande "mvn -o -q verify"` → « Votre harnais attrape 7 défauts sur 13 (54 %) ; les 6 trous : … ». S'appuie sur PIT (l'idée du mutation testing), ArchUnit, PMD, SpotBugs, Maven. Nom vérifié libre sur GitHub et PyPI le 28/11/2026 (« harness-probe » était pris sur GitHub par deux dépôts, dont un sur un sujet voisin).

**Objectif du talk (ce que le public fera lundi) :** lancer `harness-mutant` sur son projet, lire ses trous, et fermer le premier.

**Promesse (« vous repartirez avec ») :**
1. La réponse mesurée à la question de Böckeler sur un vrai harnais : l'agent ne contourne pas les règles, elles ne voient pas ses défauts.
2. Un outil open source pour mesurer la couverture de votre harnais en une commande, avec un catalogue de défauts extensible.
3. Deux garde-fous gratuits : le droit d'abandonner, le diff vide refusé.

**Le message en une phrase :** si vos règles ne sonnent jamais, ne vous en félicitez pas : mesurez ce qu'elles attrapent.

## Table par slide

| n° | étape | titre-phrase | objectif : le public pense… | preuve | durée |
|---|---|---|---|---|---|
| 1 | Départ | Mon harnais était aveugle, pas mon agent. | « Contre-intuitif, et il y a un outil au bout. » | 180 tâches, 0 règle qui sonne ; 0/34 défauts de revue vus | 1 min 30 |
| 2 | Départ | Vous avez mis votre agent de code dans un harnais : tests, linters et règles qui bloquent tant que c'est rouge. | « C'est exactement mon équipe. » | mon harnais : 11 règles ArchUnit + hook (RATCHET.md) | 2 min |
| 3 | Départ | Sur 180 tâches, mes 11 règles n'ont jamais sonné. | « Chez moi non plus, et j'en étais content. » | mesures/README.md : 180 passages, 0 violation, 30/30 verts | 1 min 30 |
| 4 | Problème | Un harnais muet ne dit pas si votre code est bon ou si vos capteurs sont aveugles. | « Je ne sais pas ce que mon harnais attrape. » | Böckeler, martinfowler.com, 02/04/2026 | 2 min |
| 5 | Problème | Ce n'est pas l'agent qui triche : 0 contournement sur 144 tickets qui exigent ce qu'une règle interdit. | « Le risque n'est pas la triche. » | contournement/README.md : 0/144, 144 citent la règle, 18 décisions rendues | 2 min 30 |
| 6 | Problème | Deux relecteurs trouvent 34 défauts dans 10 diffs de l'agent ; mon harnais n'en voit aucun. | « Mon harnais ne regarde pas là où l'agent se trompe. » | revue-croisee/ : agent de revue 31 constats, juge à l'aveugle 21, 34 défauts, 0 vu par règles / PMD-SpotBugs / tests | 3 min |
| 7 | Problème | Du java.time propre, et une livraison annoncée un jour trop tôt. | « Voilà à quoi ressemble un défaut d'agent en 2026. » | Order.java:87, OrderTest.java:25-26 ; format mm/jj : 20 tests verts | 2 min |
| 8 | Problème | Sur 20 défauts injectés, mes règles n'en attrapent aucun : 13 passent sans bruit. | « Même mécaniquement, c'est aveugle. » | aveugle/defauts-resultats.jsonl : 0 / 4 / 3 / 13 | 2 min |
| 9 | Cible | Connaître la couverture de votre harnais comme celle de vos tests. | « C'est ça que je veux. » | (la cible, pas de chiffre) | 1 min 30 |
| 10 | Comment | harness-mutant injecte des défauts réalistes et compte ce que votre harnais attrape. | « Une commande, je peux le faire lundi. » | outil/exemples/sortie-projet-du-talk.txt : 7/13, tests 7, règles 0 ; démo live | 3 min 30 |
| 11 | Comment | Dans le code que l'agent vient d'écrire, mon harnais attrape 3 défauts sur 40. | « L'outil retrouve sans relecteur ce que la revue avait vu. » | revue-croisee/harnais-lignes-agent/ : règles 0, tests 3, trous 37 (30 tests affaiblis, 7 production, dont 4 signalés par la revue) | 2 min |
| 12 | Comment | Une règle et deux tests : le score passe de 7 à 10 sur 13. | « Chaque trou se ferme ; ce qui reste, c'est le travail de PIT. » | outil/exemples/fermer-les-trous.patch, sortie-apres-patch.txt | 2 min 30 |
| 13 | Comment | Mesurez votre harnais, laissez l'agent abandonner, refusez le diff vide. | « Trois gestes, dont un outil. » | ÷ 2,2 (V3, 48/48) ; 15 passages vides comptés réussis | 2 min |
| 14 | Comment | Mon agent ne trichait pas : mes règles regardaient les erreurs d'hier. Mesurez les vôtres. | La phrase à retenir, et la commande à taper. | dépôt public, limites | 2 min |

Total : 30 min.

## Quickie 20 min (10 slides)

1, 2, 4, 6, 7, 9, 10, 12, 13, 14 : on garde le chemin (départ → problème → cible → comment) et la démo ; on retire les 180 tâches (dites en une phrase sur la 2), la triche (dite en une phrase sur la 6), l'injection du banc (8, remplacée par la démo) et les 10 copies (11).

## Skim test (titres lus seuls)

Mon harnais était aveugle, pas mon agent. Vous avez mis votre agent de code dans un harnais : tests, linters et règles qui bloquent tant que c'est rouge. Sur 180 tâches, mes 11 règles n'ont jamais sonné. Un harnais muet ne dit pas si votre code est bon ou si vos capteurs sont aveugles. Ce n'est pas l'agent qui triche : 0 contournement sur 144. Deux relecteurs trouvent 34 défauts dans 10 diffs de l'agent ; mon harnais n'en voit aucun, comme ce java.time propre qui livre un jour trop tôt ; sur 20 défauts injectés, mes règles n'en attrapent aucun. Je veux connaître la couverture de mon harnais comme celle de mes tests : harness-mutant injecte des défauts et compte ce qui sonne ; dans le code que l'agent vient d'écrire, mon harnais attrape 3 défauts sur 40 ; une règle et deux tests font passer le score de 7 à 10 sur 13. Mesurez votre harnais, laissez l'agent abandonner, refusez le diff vide : mes règles regardaient les erreurs d'hier, mesurez les vôtres.

## Sources des chiffres

- `mesures/README.md` : 180 passages, 0 violation ajoutée, 30/30 tests verts, dette nettoyée 30/30, +59 %.
- `mesures/these-a/contournement/` : 144 passages, 0 contournement, 1 tentative bloquée, 18 décisions rendues, V3 48/48, coût ÷ 2,2.
- `mesures/these-a/revue-croisee/` (28/11/2026) : agent de revue 31 constats, juge à l'aveugle 21, 34 défauts uniques dont 18 trouvés par les deux et 6 majeurs ; vus par les 11 règles 0, par PMD/SpotBugs 0 (2 avertissements GuardLogStatement sur les mêmes lignes, sans rapport), par les tests 0 (témoins verts) ; harness-mutant sur les lignes de l'agent : 40 défauts, 0 attrapé par les règles, 3 par les tests, 37 trous.
- `mesures/these-a/aveugle/` (25/11/2026) : 20 défauts injectés (0 règles, 4 outils, 3 tests, 13 personne), 15 passages invalides. L'ancienne revue simulée (38 remarques, 0 vue) est gardée comme historique.
- `outil/exemples/` : sorties réelles de harness-mutant (7/13 avant, 10/13 après le patch).
- Böckeler, « Harness engineering for coding agent users », martinfowler.com, 02/04/2026 ; ImpossibleBench, arXiv 2510.20270.
