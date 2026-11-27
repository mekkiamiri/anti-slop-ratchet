# Plan du deck v2 : « Mon harnais était aveugle, pas mon agent »

Tools-in-Action, 30 min, 16 slides. Source : `slides/slides.html` → `docs/slides/index.html`.

**Le message en une phrase :** vos règles ne sonnent jamais ; pas parce que l'agent triche (il ne triche pas), mais parce qu'elles regardent les erreurs d'hier et que les siennes sont ailleurs ; voici comment mesurer votre harnais comme vous mesurez vos tests.

Titres proposés (≤ 60 caractères) :
1. « Mon harnais était aveugle, pas mon agent » (41) : **retenu**, il dit la conclusion et réfute l'idée reçue.
2. « Vos règles ne sonnent jamais. Bonne nouvelle ? » (47)
3. « Mesurez votre harnais comme vous mesurez vos tests » (51)

Arc : situation (1-3) · complication (4 : le silence, qualité ou cécité ?) · hypothèse 1 réfutée (5-9) · hypothèse 2 confirmée (10-14) · résolution (15-16).

| n° | titre-phrase | ce que je veux dire | durée |
|---|---|---|---|
| 1 | Mon harnais était aveugle, pas mon agent. | Je vais raconter pourquoi mes règles ne sonnaient jamais, et ce n'était pas la faute de l'agent. | 1 min |
| 2 | Si vos capteurs ne sonnent jamais, personne ne sait si c'est bon signe. | La question est de Böckeler (martinfowler.com, 02/04/2026), elle est ouverte, et elle demande une « couverture » du harnais. | 1 min 30 |
| 3 | J'ai changé 11 remarques de revue en 11 règles qui bloquent l'agent. | Mon harnais en une slide : règle testée + hook qui empêche de rendre la main. | 1 min 30 |
| 4 | Sur 180 tâches, mes règles n'ont jamais sonné. | 0 erreur du catalogue ; seul effet : dette nettoyée 30/30 pour +59 %. Point de départ, pas le sujet. | 1 min 30 |
| 5 | Peut-être que l'agent triche : on sait que les modèles touchent aux tests. | ImpossibleBench rend l'hypothèse plausible : mon zéro pourrait être truqué. | 1 min 30 |
| 6 | Je lui ai donné 12 tickets qu'on ne peut pas faire sans casser une règle. | 12 tickets en conflit avec une règle, 3 variantes, 2 modèles, 144 passages. | 2 min |
| 7 | Il n'a jamais contourné une règle : il la cite. | 0 contournement sur 144, 1 tentative bloquée par deny, 144 réponses citent la règle. | 2 min |
| 8 | Bloqué, il ne triche pas : il plaide. | Citation réelle « je ne la modifie pas sans votre accord » ; 18 passages laissent le build rouge et rendent la décision. | 2 min 30 |
| 9 | Lui donner le droit d'abandonner coûte 2,2 fois moins cher. | Une phrase dans le ticket : 48/48 refus nets, coût ÷2,2, durée ÷3 ; sans elle, Opus trouve plus de variantes conformes. | 2 min |
| 10 | Peut-être que mes règles regardent les erreurs d'hier. | Hypothèse 2 : les règles viennent du code humain, l'agent se trompe ailleurs. | 1 min |
| 11 | J'ai fait relire 10 diffs comme par un senior, puis injecté 20 défauts. | Deux mesures de couverture du harnais : revue (simulée) et injection de défauts (mutation testing du harnais). | 2 min |
| 12 | Mes règles ont vu 0 remarque sur 38, et 13 défauts sur 20 passent sans bruit. | Règles 0/38 et 0/20, outils 4/20, tests 3/20, personne 13/20 ; les cousins des règles passent aussi. | 2 min 30 |
| 13 | Du java.time propre, et une livraison annoncée un jour trop tôt. | Order.java:87 fige l'UTC, OrderTest.java:25-26 fige le bug ; R09 satisfaite. | 2 min 30 |
| 14 | « 0 violation, tests verts » : c'est aussi ce que rend un agent qui n'a rien fait. | 15 passages sans écriture comptés « réussis » : il faut contrôler le diff vide. | 2 min |
| 15 | Mesurez votre harnais comme vous mesurez vos tests. | 3 gestes (droit d'abandon, injection de défauts, diff vide) + limites (petit projet, 2 modèles, revue simulée, défauts choisis). | 3 min |
| 16 | L'agent ne triche pas : vos règles regardent les erreurs d'hier. | La phrase à garder, et tout se rejoue dans `mesures/`. | 1 min 30 |

Total : 30 min.

## Skim test (titres lus seuls)

Si vos capteurs ne sonnent jamais, personne ne sait si c'est bon signe. J'ai changé 11 remarques de revue en 11 règles ; sur 180 tâches, elles n'ont jamais sonné. Peut-être que l'agent triche : je lui ai donné 12 tickets qu'on ne peut pas faire sans casser une règle ; il n'a jamais contourné, il cite la règle, il plaide, et lui donner le droit d'abandonner coûte 2,2 fois moins cher. Peut-être alors que mes règles regardent les erreurs d'hier : relecture et 20 défauts injectés ; elles voient 0 remarque sur 38 et 13 défauts passent sans bruit, comme ce java.time propre qui livre un jour trop tôt ; et « 0 violation, tests verts », c'est aussi un agent qui n'a rien fait. Mesurez votre harnais comme vos tests : l'agent ne triche pas, vos règles regardent les erreurs d'hier.

Résultat : l'argument tient de bout en bout. Accrocs corrigés : (a) le titre de la slide 6 disait « 12 tickets impossibles sans casser une règle » (contresens) ; (b) la slide de fin disait « ne sonnent pas parce que l'agent triche, mais… » (ambigu) ; (c) le chiffre 374 du titre mélangeait des passages où les règles sonnent exprès (tickets impossibles) : remplacé par « 180 tâches ordinaires ». Écart assumé : la slide 9 (droit d'abandon) est un cadeau pratique plus qu'une étape de la preuve, et la slide 15 porte deux idées (gestes + limites), comme demandé par le plan.

## Sources des chiffres

- `mesures/README.md` : 180 passages, 0 erreur du catalogue, dette nettoyée 30/30, +59 % de coût.
- `mesures/these-a/contournement/README.md` : 144 passages, 0 contournement, 1 tentative bloquée, 18 violations laissées, V3 48/48, coût ÷2,2, durée ÷3, Opus 33/48 contre 18/48.
- `mesures/these-a/aveugle/README.md` : 38 remarques (0 vue), 20 défauts (0 règles, 4 outils, 3 tests, 13 personne), 15 passages invalides, 414 lignes, couverture > 92 %.
- Böckeler, « Harness engineering for coding agent users », martinfowler.com, 02/04/2026 (citation vérifiée sur la page).
- ImpossibleBench, arXiv 2510.20270 (2025) (résumé vérifié).
