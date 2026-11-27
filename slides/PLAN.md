# Plan du deck v2 : « Mon harnais était aveugle, pas mon agent »

Tools-in-Action, 30 min, 16 slides. Source : `slides/slides.html` → `docs/slides/index.html`.

**Public :** tech leads, architectes et développeurs qui encadrent des agents de code avec des règles (linters, ArchUnit, hooks), niveau intermédiaire à avancé.

**Objectif du talk (ce que le public fera lundi) :** mesurer la couverture de son propre harnais, en injectant quelques défauts réalistes et en comptant ce qui sonne, au lieu de se rassurer parce que ses règles ne sonnent jamais.

**Promesse (« vous repartirez avec ») :**
1. La réponse mesurée à la question de Böckeler sur ce projet : l'agent ne contourne pas les règles (0 contournement sur 144 passages), mais elles n'attrapent aucun des 20 défauts injectés.
2. Une méthode pour mesurer son harnais : injecter des défauts réalistes, comme le mutation testing le fait pour les tests, et compter qui sonne (rejouable avec `injecter.py`).
3. Deux garde-fous gratuits : donner à l'agent le droit d'abandonner (coût ÷ 2,2) et refuser un passage dont le diff est vide.

**Le message en une phrase :** vos règles ne sonnent jamais ; pas parce que l'agent triche (il ne triche pas), mais parce qu'elles regardent les erreurs d'hier et que les siennes sont ailleurs ; mesurez votre harnais comme vous mesurez vos tests.

**Tension (une phrase) :** un harnais muet peut vouloir dire « code propre » ou « capteurs aveugles », et rien dans le harnais ne permet de trancher (slide 2, gardée vivante jusqu'à la slide 12).

Titres proposés (≤ 60 caractères) :
1. « Mon harnais était aveugle, pas mon agent » (41) : **retenu**, il dit la conclusion et réfute l'idée reçue.
2. « Vos règles ne sonnent jamais. Bonne nouvelle ? » (47)
3. « Mesurez votre harnais comme vous mesurez vos tests » (51)

Arc : situation (1-3) · complication (4 : le silence, qualité ou cécité ?) · hypothèse 1 réfutée (5-9) · hypothèse 2 confirmée (10-14) · résolution (15-16).

| n° | titre-phrase | objectif : le public pense… | preuve | durée |
|---|---|---|---|---|
| 1 | Mon harnais était aveugle, pas mon agent. | « Contre-intuitif : je veux savoir pourquoi. » | 180 tâches, 0 règle qui sonne, 13/20 défauts invisibles | 1 min |
| 2 | Si vos capteurs ne sonnent jamais, personne ne sait si c'est bon signe. | « Je me suis déjà posé la question. » | citation de Böckeler, martinfowler.com, 02/04/2026 | 1 min 30 |
| 3 | J'ai changé 11 remarques de revue en 11 règles qui bloquent l'agent. | « C'est un vrai harnais, comme le mien. » | une règle (R08) + le hook PostToolUse/Stop (RATCHET.md) | 1 min 30 |
| 4 | Sur 180 tâches, mes règles n'ont jamais sonné. | « Bonne nouvelle… ou pas ? » | 180 passages, 0 erreur du catalogue, dette nettoyée 30/30 (mesures/README.md) | 1 min 30 |
| 5 | Peut-être que l'agent triche : on sait que les modèles touchent aux tests. | « Plausible, j'ai lu ça. » | ImpossibleBench, arXiv 2510.20270 | 1 min 30 |
| 6 | Je lui ai donné 12 tickets qui exigent ce qu'une règle interdit. | « Le test est honnête : il avait toutes les raisons de tricher. » | protocole : 12 tickets, 3 variantes, 2 modèles, 144 passages | 2 min |
| 7 | Il n'a jamais contourné une règle : il la cite. | « Il ne triche pas. » | 0 contournement sur 144, 1 tentative bloquée | 2 min |
| 8 | Bloqué, il ne triche pas : il plaide. | « Le vrai risque, c'est le blocage, pas la triche. » | citation réelle (I07, Sonnet 5.5), 18 passages build rouge | 2 min 30 |
| 9 | Lui donner le droit d'abandonner coûte 2,2 fois moins cher. | « Une phrase à ajouter dès lundi. » | V3 : 48/48 refus nets, coût ÷ 2,2 | 1 min |
| 10 | Peut-être que mes règles regardent les erreurs d'hier. | « Et si c'était ça ? » | les 11 règles viennent de revues de code humain | 1 min |
| 11 | J'ai fait relire 10 diffs comme par un senior, puis injecté 20 défauts. | « La méthode est réutilisable chez moi. » | protocole (aveugle/README.md) | 2 min |
| 12 | Mes règles ont vu 0 remarque sur 38, et 13 défauts sur 20 passent sans bruit. | « Mon harnais est peut-être aveugle aussi. » | tableau des résultats | 3 min |
| 13 | Du java.time propre, et une livraison annoncée un jour trop tôt. | « Voilà à quoi ressemble un défaut de 2026. » | Order.java:87, OrderTest.java:25-26 | 2 min 30 |
| 14 | « 0 violation, tests verts » : c'est aussi ce que rend un agent qui n'a rien fait. | « Je vérifie le diff dès demain. » | 15 passages vides comptés réussis | 2 min |
| 15 | Mesurez votre harnais comme vous mesurez vos tests. | « Je repars avec une méthode et deux garde-fous. » | les 3 gestes + limites | 3 min |
| 16 | L'agent ne triche pas : vos règles regardent les erreurs d'hier. | La phrase à retenir. | dépôt public, données brutes | 1 min 30 |

Total : 30 min.

## Skim test (titres lus seuls)

Mon harnais était aveugle, pas mon agent. Si vos capteurs ne sonnent jamais, personne ne sait si c'est bon signe. J'ai changé 11 remarques de revue en 11 règles qui bloquent l'agent ; sur 180 tâches, elles n'ont jamais sonné. Peut-être que l'agent triche : je lui ai donné 12 tickets qui exigent ce qu'une règle interdit ; il n'a jamais contourné, il cite la règle ; bloqué, il plaide ; et lui donner le droit d'abandonner coûte 2,2 fois moins cher. Peut-être alors que mes règles regardent les erreurs d'hier : relecture de 10 diffs et 20 défauts injectés ; elles voient 0 remarque sur 38 et 13 défauts passent sans bruit, comme ce java.time propre qui livre un jour trop tôt ; et « 0 violation, tests verts », c'est aussi un agent qui n'a rien fait. Mesurez votre harnais comme vos tests : l'agent ne triche pas, vos règles regardent les erreurs d'hier.

Résultat : l'argument tient de bout en bout, la tension posée en 2 n'est résolue qu'en 12. Accrocs de la revue 1 : voir `slides/REVUE.md`.

## Sources des chiffres

- `mesures/README.md` : 180 passages, 0 erreur du catalogue, dette nettoyée 30/30, +59 % de coût.
- `mesures/these-a/contournement/README.md` et `donnees.jsonl` : 144 passages, 0 contournement, 1 tentative bloquée, 18 violations laissées, V3 48/48, coût ÷ 2,2 (0,245 $ contre 0,111 $ par passage), durée ÷ 3,1, Opus 33/48 contre Sonnet 18/48.
- `mesures/these-a/aveugle/README.md`, `revue.json`, `defauts-resultats.jsonl` : 38 remarques (0 vue), 20 défauts (0 règles, 4 outils, 3 tests, 13 personne), 15 passages invalides, 414 lignes, couverture > 92 %.
- Böckeler, « Harness engineering for coding agent users », martinfowler.com, 02/04/2026 (citation vérifiée sur la page).
- ImpossibleBench, arXiv 2510.20270 (23/10/2025) (phrase citée vérifiée dans le résumé).
