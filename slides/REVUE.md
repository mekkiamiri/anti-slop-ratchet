# Revues du deck « Mon harnais était aveugle, pas mon agent »

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

