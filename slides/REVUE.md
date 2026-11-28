# Revues du deck « Mon harnais était aveugle, pas mon agent »

## Deck v3 (28/11/2026, branche `deck-v3`) : le chemin en 4 étapes, l'outil, la revue croisée

Constat de départ (Mekki, sur le deck v2) : « en lisant les diapos je ne comprends pas le point de départ,
le point cible, le problème et comment faire » ; « il manque un outil qu'on met sur notre GitHub ».

Ce qui change :

| Avant (v2) | Après (v3) |
|---|---|
| Arc « hypothèse 1 réfutée, hypothèse 2 confirmée », 16 slides | 14 slides, chacune dans une étape affichée en surtitre : Départ (1-3) → Problème (4-8) → Cible (9) → Comment (10-14) |
| Preuve principale de cécité : revue simulée (38 remarques d'un seul agent, 0 vue) | Revue croisée sur les mêmes 10 diffs : agent de revue `gsd-code-reviewer` + juge à l'aveugle (grille écrite avant, diffs anonymisés) ; 34 défauts, 6 majeurs (tous vus par les deux), **0 vu par le harnais** (règles, PMD/SpotBugs, tests). L'ancienne revue devient un historique. |
| Méthode « rejouable avec injecter.py » | Outil livré `harness-mutant` (outil/, Python stdlib, 16 tests, CI) : `harness-mutant --projet . --commande "mvn -o -q verify"` → 7/13, puis 10/13 après une règle et deux tests ; `--diff` sur les lignes de l'agent : 3/40 |
| Promesse : une méthode + deux garde-fous | Promesse : l'outil + la méthode pour fermer un trou + deux garde-fous |

Banc de devkit : le code de notation du banc spec-driven n'existe que dans le dossier de travail (pas sous
`02-Personal`, où `lab/benchmarks/spec-driven` ne contient que la spec) ; il n'a pas été lu ni recopié. Seule la
méthode générique, décrite dans la page d'état des bancs, a été reprise : sorties renommées par des lettres,
juge à l'aveugle, grille fixée avant, défauts pondérés par gravité ([grille-juge.md](../mesures/these-a/revue-croisee/grille-juge.md)).
Aucun chiffre, nom ou contenu de l'appli du travail.

### Test de clarté

Protocole : un agent relecteur neuf reçoit **seulement** le texte des slides (titres + corps, sans notes ni
PLAN.md) et le profil « développeur Java intermédiaire qui n'a jamais entendu parler du sujet ». Il répond
en 5 lignes (départ, problème, cible, comment, outil) et dit ce qui est flou. Comparaison avec PLAN.md.

**Tour 1** (14 slides, première version) :

1. Départ : « j'ai mis mon agent de code sous contrôle (tests, linters, règles ArchUnit tirées de mes revues, un hook qui relance tout). Comme rien ne passe au rouge, je pense que le code produit est bon. »
2. Problème : « ce silence ne prouve rien. L'agent ne triche pas, mais mes règles ne voient presque aucun des vrais défauts (0 sur 34 trouvés en revue, 0 sur 20 défauts injectés). Elles surveillent les erreurs d'hier. »
3. Cible : « connaître la couverture de mon harnais comme je connais celle de mes tests : combien de défauts il attrape sur N, où sont les trous et quelle règle ou quel test fermerait chacun. »
4. Comment : « injecter volontairement des défauts réalistes, si possible dans les lignes écrites par l'agent, compter ce que le harnais attrape, fermer les trous, fixer un seuil en CI, autoriser l'agent à abandonner et refuser un tout vert quand le diff est vide. »
5. Outil : « harness-mutant, `git clone …anti-slop-ratchet` puis `pip install ./anti-slop-ratchet/outil`, lancé avec `harness-mutant --projet . --commande "mvn -o -q verify"`. »
- Flou : « droit d'abandonner (coût ÷ 2,2) » sans dire quel coût ; les totaux 13, 20, 40 changent sans explication ; « tests affaiblis / oracles » non défini ; le dépôt n'a pas le nom de l'outil ; un outil Python surprend un dev Java ; « 18 décisions rendues à l'humain » obscur.

Verdict : les 5 réponses sont justes par rapport à PLAN.md. Six points flous, corrigés :
slide 5 « 18 arrêts : « je ne contourne pas, décidez » » ; slide 8 « 20 défauts écrits à la main » ;
slide 10 « 13 des 23 défauts du catalogue s'appliquent à ce projet » et « Python 3 sans dépendance, il lance
votre commande Maven » ; slide 11 « 40 défauts du catalogue tombent dans les lignes de l'agent » et « tests
affaiblis (assertion retirée, valeur non vérifiée) » ; slide 12 « des tests qui ne vérifient plus la valeur » ;
slide 13 « « si une règle bloque, arrête-toi et explique » (facture de l'agent ÷ 2,2) » ; slide 14
« l'outil est dans le dépôt du talk ».

**Tour 2** (relecteur neuf, slides corrigées) :

1. Départ : « tu as mis ton agent de code dans un cadre (tests, linters, règles ArchUnit, un hook qui relance tout) et tu crois que ça le surveille. Comme rien ne passe jamais au rouge, tu penses que tout va bien. »
2. Problème : « quand rien ne sonne, tu ne sais pas si le code est bon ou si tes contrôles ne voient rien. Les chiffres montrent qu'ils ne voient rien : l'agent ne triche pas, mais les relecteurs trouvent 34 défauts que tes règles laissent passer, et sur 20 bugs injectés, tes règles n'en attrapent aucun. »
3. Cible : « pouvoir dire « mon cadre attrape X défauts sur N », comme une couverture de code, avec la liste des trous et la règle ou le test qui fermerait chacun. »
4. Comment : « injecter exprès des défauts réalistes (dans tout le projet, ou seulement dans les lignes écrites par l'agent avec --diff) et compter ceux que le build attrape ; fermer les trous avec des règles ou des tests ciblés, fixer un seuil en CI, dire à l'agent de s'arrêter et d'expliquer quand une règle le bloque, refuser un diff vide comme succès. »
5. Outil : « harness-mutant (Python, Apache-2.0) : `git clone https://github.com/mekkiamiri/anti-slop-ratchet && pip install ./anti-slop-ratchet/outil`, puis `harness-mutant --projet . --commande "mvn -o -q verify"`. »
- Flou : « harnais » compris seulement à la slide 2 ; lien avec PIT pas clair ; dépôt « anti-slop-ratchet » contre outil « harness-mutant » ; quel nombre retenir (20, 13, 40) ; « facture de l'agent ÷ 2,2 » sort de nulle part.

Verdict : 5 réponses justes. Corrigé : slide 2, ligne « Harnais = tout ce qui entoure l'agent pour vérifier son code » ;
slide 12, PIT défini (« l'outil Java de mutation testing, qui vérifie que vos tests échouent quand le code change ») ;
slide 11, « le N dépend du projet : comparez votre score à lui-même » ; slide 13, « coût des appels au modèle ÷ 2,2, mesuré » ;
slide 14, « harness-mutant est dans le dossier outil/ du dépôt du talk ».

**Tour 3** (relecteur neuf, dernier tour) :

1. Départ : « j'ai mis mon agent de code dans un cadre (tests, linters, règles ArchUnit, un hook qui relance tout) et comme rien ne sonne jamais, je me dis que tout va bien. »
2. Problème : « le silence ne prouve rien. Les règles ne détectent aucun des vrais défauts trouvés en revue (0 sur 34) ni aucun des défauts injectés à la main (0 sur 20). Ce n'est pas l'agent qui triche, ce sont mes règles qui ne regardent pas au bon endroit, par exemple un bug de fuseau horaire avec un code java.time pourtant propre. »
3. Cible : « connaître la couverture de mon harnais comme je connais celle de mes tests : j'attrape X défauts sur N, voici les trous et la règle qui fermerait chacun. »
4. Comment : « injecter des défauts réalistes (le projet entier ou seulement les lignes écrites par l'agent), compter ceux que le build attrape, fermer les trous avec des règles ou des tests (et PIT pour les tests faibles), mettre un seuil en CI, demander à l'agent de s'arrêter quand une règle le bloque, refuser un diff vide présenté comme un succès. »
5. Outil : « harness-mutant : `git clone https://github.com/mekkiamiri/anti-slop-ratchet && pip install ./anti-slop-ratchet/outil`, puis `harness-mutant --projet . --commande "mvn -o -q verify"`. »
- Flou : les tests font-ils partie du harnais (le titre de la slide 2 ne parlait que de règles) ; beaucoup de totaux différents (13, 20, 23, 34, 40) ; « coût ÷ 2,2 » sans explication ; « refusez le diff vide » sans slide qui l'amène.

Verdict : **réussi aux trois tours** (les 5 réponses sont justes et précises par rapport à PLAN.md à chaque
tour ; dès le tour 2, le relecteur cite aussi `--diff`, le seuil en CI et PIT). Dernières retouches après le
tour 3, sans nouveau tour (3 au maximum) : titre de la slide 2 « tests, linters et règles qui bloquent… » ;
slide 13 « (48 tickets : coût des appels au modèle ÷ 2,2) » et « (vécu : 15 passages vides comptés réussis) ».
Reste assumé : plusieurs totaux de défauts (20 du banc, 34 de la revue, 13 et 40 de l'outil). Chaque slide dit
d'où vient le sien ; la note de la slide 11 dit lequel retenir (le vôtre, comparé à lui-même dans le temps).

### Grille du comité (v3)

| Critère | v2 | v3 | Justification |
|---|---|---|---|
| Unicité | 4 | 5 | Un outil installable qui répond à la question ouverte de Böckeler (couverture du harnais), adossé à des mesures publiées : rien d'équivalent dans les programmes 2026. |
| Légitimité | 3 | 3 | Inchangée : pas de nouveau fait (PR non fusionnées, pas de scène renseignée). |
| Promesse | 4 | 5 | « Vous repartirez avec » : un outil, une commande, un catalogue à étendre, et deux garde-fous chiffrés. |
| Concret | 5 | 5 | 374 passages + revue croisée + outil testé en CI + sorties réelles. |
| Actualité | 5 | 5 | « Harness engineering » reste le sujet ; l'angle « mesurer le harnais » est mûr. |
| Clarté | 4 | 5 | Chemin en 4 étapes visible sur chaque slide ; test de clarté réussi (5 réponses justes dès le tour 1). |
| Risque speaker | 3 | 3 | Démo de l'outil en direct (1 min 43, sortie enregistrée en plan B) ; reste à 3 sans expérience de scène renseignée. |
| Format | 5 | 5 | 14 slides pour 30 min (table de PLAN.md à 30 min pile), liste Quickie 20 min. |
| **Total** | **33** | **36** | Seuil 32 atteint, aucun critère sous 3. |

### Ce qui reste à Mekki (v3)

1. **Relire les 6 défauts majeurs** de la revue croisée (`mesures/these-a/revue-croisee/README.md`, 15 min) : ce sont les constats que les deux relecteurs (deux agents) partagent ; une confirmation humaine renforce la slide 6.
2. **Nom de l'outil** : `harness-mutant` retenu (libre sur GitHub et PyPI le 28/11/2026). Autres noms libres vérifiés : `blindspot-probe`, `harness-catch`. `harness-probe` est pris sur GitHub (deux dépôts, dont un qui mesure déjà « harness » au sens modèle + outillage). Si changement : `outil/pyproject.toml`, `outil/harness_mutant/`, slides 10-14, PLAN, propositions.
3. **Publier sur PyPI** (facultatif) : aujourd'hui l'installation passe par `git clone` + `pip install ./outil`.
4. Expérience de scène, accord employeur, référence du talk ArchUnit de Devoxx BE 2026, vidéo de secours : inchangés (voir plus bas).

---

## Historique : revues du deck v2

Trois revues successives avant la vérification de Mekki (28/11/2026), sur la branche `deck-v2`. Gravité : 🔴 casse dans la salle · 🟡 coûte de la force · ⚪ goût. Aucune nouvelle mesure n'a été lancée : tout chiffre vient des fichiers de `mesures/`.

## Revue 1 : l'argument

Grille (deck-review-rubric) avant corrections : argument 4/5 · preuves 4/5 · densité 4/5 · arc 3/5 (hypothèse 1 longue : 5 slides, 9 min 30, dont un détour) · honnêteté 3/5 (slide 6).

Problèmes trouvés :

| Gravité | Slide | Problème | Correction |
|---|---|---|---|
| 🔴 | 6 | Contresens : « 12 tickets qu'on ne peut pas faire sans casser une règle » (ou « qu'on ne peut faire qu'en cassant une règle »). C'est faux : on peut refuser, ou livrer une variante conforme, et l'agent le fait (Opus 33/48 variantes conformes en V1+V2). Un expert le relève tout de suite, et ça affaiblit la slide 7. | Titre : « Je lui ai donné 12 tickets qui exigent ce qu'une règle interdit. » (formulation du README de la mesure). Note : ce ne sont pas des tickets impossibles, la question est « triche-t-il pour passer au vert ? ». |
| 🟡 | 9 | Le droit d'abandon est un détour pratique, pas une étape de la preuve, et il prenait 2 min dans la partie déjà la plus longue. | Ramené à 1 min : 2 chiffres au lieu de 3 (÷ 3 sur la durée retiré de la slide, gardé dans PLAN), note réduite à 3 phrases. La minute gagnée va à la slide 12 (3 min), qui doit porter la limite de la revue simulée. |
| 🟡 | PLAN | Ni objectif du talk, ni promesse, ni objectif par slide : impossible de vérifier que chaque slide sert le « lundi » du public. | Objectif, promesse, tension en une phrase et table n° · titre-phrase · objectif · preuve · durée en tête de PLAN.md. |
| 🟡 | PLAN / 15 | La promesse de la page d'objectifs listait « trois gestes » dont « viser ses règles sur les défauts de 2026 », geste qu'aucune slide ne prouve, et doublait l'injection de défauts (promesse 2 et geste). | Promesse réécrite : (1) la réponse mesurée, (2) la méthode d'injection, (3) deux garde-fous gratuits (droit d'abandon, diff vide). La slide 15 montre exactement ces trois gestes. |
| ⚪ | 1, 16 | Le titre du talk et la slide 16 disent presque la même chose. | Laissé : c'est la boucle d'ouverture et de fermeture, voulue. |

Skim test après corrections : passe (voir PLAN.md). Chaque titre est une phrase qui affirme ; les deux « Peut-être que… » (5 et 10) sont des hypothèses assumées, résolues par les titres qui suivent.

Reste : la slide 15 porte deux idées (gestes + limites). Gardé : les limites doivent être dites sur scène et une slide à part coûterait 1 min.


## Revue 2 : les preuves et l'honnêteté

Chaque chiffre des slides, des notes et de la proposition a été recompté dans les fichiers du dépôt (pas seulement dans les README) :

| Affirmation | Vérifiée dans | Résultat |
|---|---|---|
| 180 passages, 0 erreur ajoutée, 30/30 dette nettoyée, +59 % | `mesures/README.md` (0,259 / 0,163 = 1,59) | ✓ |
| 144 passages : 0 contournement, 1 tentative bloquée, 18 violations laissées | `contournement/donnees.jsonl` (recompté : V1 39+9, V2 38+9+1, V3 48) | ✓ |
| 144 réponses citent la règle | `donnees.jsonl`, champ `explique_conflit` = 144 (mots-clés, relu sur 31) | ✓, méthode dite dans la note |
| coût ÷ 2,2, durée ÷ 3 | `donnees.jsonl` : 0,2446 $ / 0,1108 $ = 2,21 ; 71,7 s / 22,9 s = 3,13 | ✓ |
| Opus 33/48 variantes conformes contre 18/48 | README contournement (16+17 contre 9+9) | ✓ |
| citation « Je ne contourne pas la règle et je ne la modifie pas sans votre accord. », 9 blocages | `donnees.jsonl`, I07 V1 Sonnet passage 2, `retours_hook_regles` = 9 | ✓ |
| 38 remarques, 0 vue ; 20 défauts : 0 / 4 / 3 / 13 | `revue.json` (38 × « personne »), `defauts-resultats.jsonl` (recompté) | ✓ |
| 8 défauts cousins d'une règle | README aveugle (D02, D05, D06, D07, D08, D09, D17, D19) | ✓ |
| `Order.java:87`, `OrderTest.java:25-26`, `2027-04-29T23:30:00Z → 2 mai` | `diffs/sonnet-A-T03-A-1.diff`, numéros de ligne recalculés depuis les hunks | ✓ ; 23:30Z le 29/04/2027 = 01:30 le 30/04 à Paris (heure d'été) |
| 15 passages invalides comptés réussis | `passages/invalides-permission-refusee.jsonl` (15 lignes) | ✓ |
| couverture > 92 %, 0 test sans assertion, 414 lignes | `synthese.json`, README | ✓ |
| Böckeler, 02/04/2026, deux citations | martinfowler.com (récupéré par curl le 28/11/2026) | ✓ ; la 2e citation coupe « and quality » par […] : fidèle |
| ImpossibleBench, « delete failing tests rather than fix the underlying bug » | arxiv.org/abs/2510.20270 (soumis le 23/10/2025) | ✓ |
| Bio : PR ouvertes vers Google ADK Java, Spring AI A2A et AG-UI | `gh search prs` | ⚠ ADK Java et Spring AI A2A : PR ouvertes ; AG-UI : PR fermée. Corrigé (« a proposé des contributions »). |
| « Talk ArchUnit donné à Devoxx BE 2026 » (notes au comité) | recherche web | ⚠ non retrouvé en ligne : gardé tel que fourni, à confirmer par Mekki (lien) |

Problèmes trouvés :

| Gravité | Où | Problème | Correction |
|---|---|---|---|
| 🔴 | slide 11 | Surclassement : « J'ai fait relire 10 diffs comme par un senior » laisse croire à une revue humaine. C'est un agent (Opus 5.5) qui joue le relecteur, une fois, sans second avis. Un expert qui le découvre en Q&A ne croit plus le reste. | Titre : « J'ai mesuré mon harnais deux fois : une revue de 10 diffs, puis 20 défauts injectés. » Point 01 : « Revue jouée par un agent (Opus 5.5), pas par un humain ». Point 02 : « qui sonne » est mécanique. |
| 🔴 | slide 12 | Le titre reposait sur « 0 remarque sur 38 », le chiffre le plus fragile (il dépend d'un relecteur simulé), alors que le plus solide est mécanique : 0 défaut injecté sur 20 et aucune règle qui sonne sur 50 copies. | Titre : « Mes règles n'attrapent aucun des 20 défauts injectés : 13 passent sans aucun bruit. » Colonnes inversées (défauts d'abord), colonne « Remarques du relecteur simulé », ligne : « Aucune règle n'a sonné sur les 50 copies : ce zéro ne dépend pas du relecteur ». Voir plus bas : la slide reste vraie quel que soit le résultat de la relecture humaine. |
| 🔴 | slides 12, 15, proposition | « Le zéro des règles ne dépend pas de ces choix » cachait que les 20 défauts ont été choisis **hors** des 11 formes visées : le 0/20 est en partie construit. | Dit sur scène (note slide 12) : le zéro n'est pas une surprise en soi ; ce qui l'est, ce sont les 8 cousins directs, que les règles ne voient pas. Même correction dans la limite de la slide 15 et dans la proposition. |
| 🟡 | slide 7 | Limite majeure de la mesure (règles qui expliquent leur raison, hook qui dit « corrige le code, pas la règle ») seulement dans la note. « bloquée par deny » : jargon. | Ligne visible « Limite : mes règles disent pourquoi elles existent, et le hook dit « corrige le code, pas la règle » » ; « bloquée par la lecture seule ». Note : « cite la règle » compté par mots-clés, 31 passages relus. |
| 🟡 | slide 16 | « L'agent ne triche pas : vos règles regardent les erreurs d'hier » généralise un projet de 414 lignes à tous les agents et toutes les règles. | « Mon agent ne trichait pas : mes règles regardaient les erreurs d'hier. Et les vôtres ? » (vrai, et c'est une question au public : l'objectif du talk). |
| 🟡 | slides 12, 15 | « c'était avant » : 2 modèles de novembre 2026, le talk sera donné en 2027. Jargon : « CPD ». | Limite « 2 modèles de novembre 2026 » + note « si un modèle plus récent sort, tout se rejoue ». « Analyse statique (PMD, SpotBugs) ». |
| ⚪ | slide 9 | « ÷ 3 » sur la durée arrondit 3,13. | Retiré de la slide en revue 1 ; gardé dans PLAN avec la valeur exacte. |

Densité : chaque slide garde une idée. Les slides 7, 11 et 12 gagnent une ligne ; calcul de hauteur à 1920×1080 (zone utile 820 px : titre 2 lignes ≈ 150 px, tableau 5 lignes ≈ 355 px, note 50 px) : tout tient. Pas vérifié dans un navigateur (consigne).

### La revue des 38 remarques est jouée par un agent : échantillon à relire par Mekki (20 min)

Pourquoi : le « 0 sur 38 » a deux moitiés. « 0 vue par les règles » est mécanique (aucune règle n'a sonné sur aucune des 50 copies, donc sur aucune remarque) et ne peut pas changer. « 38 remarques réelles » dépend du relecteur, ici un agent : c'est cette moitié qu'un humain doit confirmer.

Échantillon tiré par une règle simple et vérifiable : **la première remarque de chaque copie relue** (10 copies, donc 10 remarques, dans l'ordre de `revue.json`). Honnêteté : la règle a été choisie après avoir vu la liste des 38 remarques ; si Mekki préfère un tirage indépendant, tirer 10 numéros entre 1 et 38 et relire ceux-là. Les diffs sont dans `mesures/these-a/aveugle/diffs/`. Le chemin est relatif à `src/{main,test}/java/io/github/mekkiamiri/ratchet/`, le numéro de ligne est celui de l'arbre rendu par l'agent ; la ligne de code citée a été relue dans le diff (lignes recalculées depuis les hunks).

Pour chaque ligne (2 min) : ouvrir le diff, lire la ligne, puis remplir **Tient ?** (oui / non / discutable) et **Correction du classement** (vide si « vue par personne » est juste ; sinon : quel outil la voit).

| n° | n° dans revue.json | copie · diff | fichier:ligne | ligne de code | remarque | classement actuel | Tient ? | Correction du classement |
|---|---|---|---|---|---|---|---|---|
| 1 | #1 | `sonnet-A/T01-A-1` · `diffs/sonnet-A-T01-A-1.diff` | `order/domain/Order.java:86-88`, `order/web/OrderResponse.java:6-7` | `public BigDecimal total() {` | total() change de sens : il valait la somme des lignes, il vaut maintenant le net remisé. Le champ JSON « total » existant change de signification pour les clients de l'API, sans versionnement ni mention. | vue par personne | | |
| 2 | #3 | `sonnet-C/T02-C-1` · `diffs/sonnet-C-T02-C-1.diff` | `order/web/OrderControllerTest.java:52` | `String location = mvc.perform(post("/orders").contentType(MediaType.APPLICATION_JSON)` | La variable « location » contient le corps JSON de la réponse, pas un en-tête Location. | vue par personne | | |
| 3 | #6 | `sonnet-A/T03-A-1` · `diffs/sonnet-A-T03-A-1.diff` | `order/domain/Order.java:87` | `return createdAt.atZone(ZoneOffset.UTC).toLocalDate().plusDays(3);` | Fuseau UTC codé en dur pour une boutique en euros : une commande passée à 00h30 heure de Paris le 30 a une date de création UTC au 29, la livraison estimée affichée a un jour d'avance. | vue par personne · cousine de R09 | | |
| 4 | #10 | `sonnet-C/T04-C-1` · `diffs/sonnet-C-T04-C-1.diff` | `order/application/OrderCsvExporter.java:37`, `order/web/OrderController.java:34` | `public int export() throws IOException {` | IOException propagée jusqu'au contrôleur et non traduite par OrderExceptionHandler : 500 générique pour le client, chemin d'erreur jamais testé. | vue par personne · cousine de R01 | | |
| 5 | #16 | `sonnet-A/T05-A-1` · `diffs/sonnet-A-T05-A-1.diff` | `order/domain/Order.java:60-65` | `public void ship() {` | ship() n'est appelée que par les tests : aucun cas d'usage ni endpoint ne permet d'expédier, la règle du ticket ne peut pas se produire en production. | vue par personne | | |
| 6 | #19 | `sonnet-C/T06-C-1` · `diffs/sonnet-C-T06-C-1.diff` | `order/application/NotificationService.java:15` | `private final List<String> sent = new CopyOnWriteArrayList<>();` | Liste en mémoire sans borne dans un singleton de production : fuite mémoire lente (un message par confirmation, jamais purgé). | vue par personne | | |
| 7 | #24 | `sonnet-A/T07-A-1` · `diffs/sonnet-A-T07-A-1.diff` | `order/application/OrderService.java:65` | `.filter(o -> o.status() == OrderStatus.CONFIRMED)` | Décision métier non demandée et non signalée : le chiffre d'affaires ne compte que les commandes CONFIRMED (et exclura tout futur statut SHIPPED). | vue par personne | | |
| 8 | #28 | `sonnet-C/T08-C-1` · `diffs/sonnet-C-T08-C-1.diff` | `order/infrastructure/InMemoryOrderRepository.java:30` | `public synchronized Order save(Order order) {` | synchronized ajouté sur save() : verrou global sur toutes les écritures, qui change le modèle de concurrence existant (verrou optimiste) pour une tâche de nuit, hors du périmètre du ticket. | vue par personne | | |
| 9 | #32 | `sonnet-A/T09-A-1` · `diffs/sonnet-A-T09-A-1.diff` | `order/domain/Order.java:77` | `return subtotal().compareTo(FREE_SHIPPING_THRESHOLD) < 0 ? SHIPPING_FEE : BigDecimal.ZERO;` | Une commande vide paie 4,90 € de frais de port (sous-total 0 < 50). | vue par personne | | |
| 10 | #35 | `sonnet-C/T10-C-1` · `diffs/sonnet-C-T10-C-1.diff` | `order/domain/OrderTotalTest.java:49-55`, `order/domain/OrderTest.java:14-20` | `void decimalPricesAreSummedWithoutRoundingError()` (l. 50) ; OrderTest.java:14-20 est hors diff : fichier d'origine `src/test/java/.../order/domain/OrderTest.java` | Reprend le scénario du test existant OrderTest (somme de 0,10 et 0,20 sans erreur d'arrondi) : doublon de test, trop court pour CPD. | vue par personne | | |

Ce que le résultat change :
- **Les slides 11 et 12 ne changent pas**, quel que soit le résultat : elles disent « revue jouée par un agent », « remarques du relecteur simulé » et appuient le titre sur l'injection mécanique. Seule la phrase de la note de la slide 11 se complète : « J'en ai relu 10 moi-même : k tiennent. »
- Si une remarque est « vue » par une des 11 règles : impossible (aucune règle n'a sonné sur ces copies) ; si cela semble le cas, c'est un bug de mesure à signaler.
- Si une remarque est vue par PMD ou SpotBugs : corriger la case « 0 / 38 » de l'analyse statique dans la slide 12 et dans le README de la mesure.
- Si k < 7 sur 10 : retirer « 38 » de la proposition (garder « une revue simulée de 10 diffs ») et dire en note « l'agent relecteur exagère : j'en garde k sur 10 ».
- Résultat à reporter dans `mesures/these-a/aveugle/README.md` (section Limites) : « échantillon de 10 remarques relu par un humain le …, k tiennent ».

## Revue 3 : le comité

### Grille (8 critères sur 5, seuil 32/40, aucun sous 3)

| Critère | Avant | Après | Justification |
|---|---|---|---|
| Unicité | 4 | 4 | Mesurer le harnais lui-même (couverture, injection de défauts) : angle rare. Risque de confusion avec le talk ArchUnit de Devoxx BE 2026, désamorcé dans la 1re note. |
| Légitimité | 3 | 3 | Tech Lead, référent IA, 3 campagnes publiques ; pas mainteneur, PR proposées mais pas fusionnées. Ne monte pas sans nouveau fait. |
| Promesse | 4 | 4 | « Vous repartirez avec » : une méthode et deux garde-fous concrets, chiffrés. |
| Concret | 5 | 5 | 374 passages d'agent, données brutes, injecteur, démo live. |
| Actualité | 5 | 5 | « Harness engineering » est le sujet de 2026 ; l'angle (mesurer plutôt qu'empiler) est mûr. |
| Clarté | 3 | 4 | Avant : « harness » non défini, et la proposition anglaise gardait le contresens « 12 tickets that cannot be done without breaking a rule ». Après : harnais défini dans la 1re phrase, contresens retiré. |
| Risque speaker | 2 | 3 | Avant : aucune trace de scène dans les notes. Après : dépôt soigné avec CI, slides en ligne, format court (Tools-in-Action), démo avec plan B. Reste à 3 tant que les meetups/vidéo ne sont pas renseignés. |
| Format | 4 | 5 | Plan minuté ajouté aux notes ; la table de PLAN.md tombe sur 30 min pile (elle faisait 29 min 30 après la revue 1 : slide 15 passée à 3 min 30). |
| **Total** | **30** | **33** | Seuil atteint, aucun critère sous 3. |

### Trois membres du comité

- **L'expert blasé** : « Encore des règles ArchUnit pour le code d'IA ? On a eu ce talk à Devoxx BE. Et une revue faite par un LLM, sérieusement ? » → La 1re note répond (les règles = une slide, le sujet = la mesure du harnais) ; le titre de la slide 12 et l'abstract s'appuient sur l'injection mécanique, la revue simulée est annoncée comme telle. Il dira probablement : « Au moins il dit ses limites et publie ses données. »
- **Le généraliste** : « Je ne sais pas ce qu'est un harnais, mais "mon agent ne trichait pas" m'accroche. » → Harnais défini dans la 1re phrase de l'abstract et sur la slide 2.
- **Le défenseur de la diversité des sujets** : « Trente propositions sur les agents ; celle-ci rapporte un résultat négatif contre l'attente du speaker, avec un protocole rejouable. C'est la seule qui mesure au lieu de promettre. » → Point fort à garder. Ce qui l'aiderait encore : nommer l'employeur (industrie, peu présente en conf), si l'accord est obtenu.

### Test des 30 secondes

Titre + 1re phrase : « Mon harnais était aveugle, pas mon agent » / « J'ai changé 11 remarques de revue récurrentes en règles qui bloquent mon agent de code : c'est son harnais. » On comprend le dispositif, l'idée reçue (l'agent triche) et la conclusion inverse. Passe. Abstract FR : 915 caractères (≤ 1200), 3 paragraphes, « Vous repartirez avec : » 3 éléments.

### Un débutant comprend-il chaque slide ?

| Slide | Obstacle | Correction |
|---|---|---|
| 2 | « harnais », « capteurs » jamais définis à l'écran | Ligne ajoutée : « Harnais = tout ce qu'on met autour de l'agent : des consignes avant, des capteurs après (tests, linters, règles) » |
| 3 | « hook » | « Un hook (script branché sur l'agent) lance les règles… » |
| 7 | « deny » | corrigé en revue 2 (« lecture seule ») |
| 11 | « mutation testing » | dit en note avec sa définition (« on casse exprès, on regarde qui sonne ») ; la slide dit « défauts injectés », compréhensible seul |
| 12 | « CPD » | corrigé en revue 2 (« analyse statique ») |
| 8 | « R03 », `Optional.get()` | gardé : public Java intermédiaire ; la note explique la règle |

### Problèmes trouvés

| Gravité | Où | Problème | Correction |
|---|---|---|---|
| 🔴 | PROPOSITION-EN | Le contresens de la slide 6 survivait dans l'abstract anglais (« 12 tickets that cannot be done without breaking a rule »), raté en revue 2. | « 12 tickets that demand what a rule forbids ». Abstract réécrit sur le modèle FR. |
| 🔴 | notes au comité | Risque speaker à 2/5 : aucune trace de scène, pas de plan minuté, pas de lien vers les slides. | Notes au format de modeles.md : dépôt + CI + commandes sans modèle, slides en ligne, démo et plan B, plan minuté, Quickie possible. Expérience de scène et accord employeur laissés en champs à compléter (rien inventé). |
| 🟡 | abstract FR/EN | « harness » jargon en tête ; promesse EN listait encore « trois gestes » dans l'ancien ordre. | Harnais défini dans la 1re phrase ; promesse alignée sur PLAN.md (méthode + deux garde-fous). |
| 🟡 | PLAN | Total 29 min 30 après la revue 1. | Slide 15 à 3 min 30 (limites + gestes). |
| 🟡 | track | « Development practices » sans justification. | Track « Méthodologie et pratiques de développement », choisi parce que le sujet y est rare (dans le track IA, il serait un parmi trente). |

## Décisions qui restent à Mekki

1. **Relire l'échantillon des 10 remarques** (revue 2, 20 min), remplir « Tient ? », puis compléter la phrase de la note de la slide 11 et la section Limites du README de la mesure. Si moins de 7 sur 10 tiennent : retirer « 38 » de la proposition (voir les règles plus haut).
2. **Expérience de scène** (meetups, JUG, interne, vidéo) : seul levier pour faire passer le risque speaker de 3 à 4. Sans rien, la grille reste à 33.
3. **Accord employeur** et choix de nommer l'entreprise (atout pour le comité, à valider avec la communication) ; rien n'est nommé aujourd'hui.
4. **Talk ArchUnit de Devoxx BE 2026** : non retrouvé en ligne pendant la revue. Ajouter le titre et le lien dans la 1re note, ou écrire « un talk récent » si la référence n'est pas sûre.
5. **Vidéo de secours de la démo** : promise dans les notes, pas encore enregistrée. La copie de démo se reconstruit avec `git apply mesures/these-a/aveugle/diffs/sonnet-A-T01-A-1.diff` (vérifié avec `git apply --check`), puis `injecter.py --seulement D02` ; à répéter une fois avant d'enregistrer.
6. **Titre** : FR et EN gardés (« Mon harnais était aveugle, pas mon agent » / « My Agent Wasn't Cheating. My Harness Was Blind. »). Alternative si le comité trouve le mot « harnais » obscur : « Mesurez votre harnais comme vous mesurez vos tests ».

Grille finale : **33/40** (unicité 4, légitimité 3, promesse 4, concret 5, actualité 5, clarté 4, risque speaker 3, format 5).
