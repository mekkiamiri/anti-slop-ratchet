# Thèse A, mesure 1 : le harnais aveugle

Question : quand les 11 règles ne sonnent pas, est-ce parce que le code de l'agent est bon, ou parce
que les règles ne regardent pas là où il se trompe vraiment ?

**En une phrase : sur 38 remarques qu'un relecteur senior ferait sur 10 diffs de l'agent, le harnais
(les 11 règles + le hook) en voit 0 et PMD/CPD/SpotBugs 0 aussi. Sur 20 défauts réalistes injectés, les
règles en attrapent 0, les outils 4 et les tests existants 3 : 13 passent sans que rien ne bouge.**

Le code de l'agent est bon *au sens des règles* (0 violation sur 50 passages, comme le 22/11). Il n'est
pas sans défaut : ses défauts sont ailleurs (contrats d'API qui changent de sens, cas limites, tests à
oracle faible, exigences réinterprétées sans le dire), et aucune des 11 règles n'y regarde. Huit des
20 défauts injectés sont des cousins directs d'une règle (le même problème sous une forme de 2026),
et les règles n'en voient aucun.

## Protocole

### 1. Passages (50 valides, 25/11/2026)

`mesures/lancer.py`, étendu sans changer son comportement par défaut :
- `--garder` crée maintenant un commit et un tag `agent` dans chaque copie **avant** que le compteur
  ne touche à la copie : `git diff départ..agent` est exactement le code rendu par l'agent ;
- `--dossier-copies` : où créer les copies (sinon dossier temporaire, comme avant) ;
- `--etiquette=-xxx` : suffixe du fichier de résultats, pour ne pas mélanger les campagnes ;
- chaque ligne de résultat porte `modele_demande`.

| Lot | Projet | Condition | Modèle demandé (et servi) | Passages |
|---|---|---|---|---|
| sonnet-A | propre | A rien | Sonnet 5.5 | 10 tâches × 2 |
| sonnet-C | propre | C règles + hook | Sonnet 5.5 | 10 tâches × 2 |
| opus-A | propre | A rien | Opus 5.5 | 10 tâches × 1 |

Mêmes 10 tâches que le 22/11 ([../../taches.json](../../taches.json)). Données : [passages/](passages/).

**Passages invalides (15, écartés et relancés).** Une première série avait mis les copies sous un
dossier que l'agent de code protège en écriture : l'agent a refusé d'écrire, a décrit ce qu'il aurait
fait et a rendu la main. Le lanceur a pourtant compté ces passages « réussis » (0 violation, tests
verts, puisque rien n'avait changé). Ils sont dans [passages/invalides-permission-refusee.jsonl](passages/invalides-permission-refusee.jsonl)
et ne sont comptés nulle part. Leçon pour le talk : *0 violation et tests verts* est aussi le résultat
d'un agent qui n'a rien fait ; le diff vide doit faire partie des contrôles.

### 2. Mesure du code ajouté ([analyser.py](analyser.py))

Pour chaque copie : export de l'arbre `agent` **sans** les règles du talk ni les mauvais exemples
(`rules/`, `slopexamples/`, `.claude/`), configuration d'analyse ajoutée au pom, `mvn -o` (hors ligne),
puis croisement des rapports avec les lignes ajoutées (`git diff -U0`). Seul le nouveau compte.

Outils (tous déjà dans `~/.m2`, vérifiés) :

| Outil | Version | Hors ligne ? | Utilisation |
|---|---|---|---|
| PMD (+ CPD) par maven-pmd-plugin | 7.17.0 / 3.28.0 | oui | [regles-pmd.xml](regles-pmd.xml) : quickstart + UnitTestShouldIncludeAssert (désactivée dans quickstart, ajoutée car elle vise un défaut typique des tests d'agent ; `andExpect` compte comme assertion) ; CyclomaticComplexity niveau 1 sert à *mesurer*, pas à avertir. CPD : 50 jetons. |
| SpotBugs par spotbugs-maven-plugin | 4.10.5 / 4.10.5.0 | oui | effort Max, seuil Low (le plus bavard : on donne sa chance à l'outil) |
| JaCoCo | 0.8.14 | oui | couverture des lignes ajoutées exécutables, par tous les tests (projet + agent) |
| Error Prone | 2.44.0 | **non** | présent dans `~/.m2`, mais Maven hors ligne refuse de le résoudre : le jar est marqué comme téléchargé depuis un autre dépôt que le miroir configuré (« present, but unavailable »). Pas contourné, comme demandé. Error Prone aurait vu D06 (`MisusedWeekYear`), voir limites. |
| PIT | - | absent | non téléchargé, comme demandé |

Heuristiques simples et explicites (constantes `MOTIF_*` d'analyser.py) :
- **nouveau type / nouvelle méthode** : déclaration sur une ligne ajoutée, dont le nom n'existait pas au départ ;
- **interface à une seule implémentation** : nouvelle interface de `src/main` avec exactement une classe `implements` dans `src/main` ;
- **assertion** : appel à `assert*`, `fail`, `verify`, `andExpect`, `expectThrows` dans le corps du test (ou appel à une méthode d'aide de la classe qui en contient) ;
- **cas limite** (sur le nom et le corps du test, insensible à la casse) : *null/vide* (`null`, `empty`, `vide`, `blank`, `absent`, `missing`, `isEmpty`…), *erreur* (`exception`, `throw`, `invalid`, `not found`, `404`, `isBadRequest`, `déjà`…), *frontière* (`exactly`, `exactement`, `limite`, `seuil`, `boundary`, `negative`…) ;
- **code mort** : méthode ajoutée dans `src/main`, hors méthodes appelées par le framework (`@Override`, `@*Mapping`, `@Scheduled`, `@Bean`…), dont le nom n'est appelé nulle part ailleurs (« jamais appelée ») ou seulement depuis `src/test` (« seulement par les tests ») ; type ajouté jamais référencé hors de son fichier (types Spring exclus).

### 3. Revue simulée ([revue.json](revue.json))

10 copies, une par tâche, choisies **avant** de les lire : passage 1 de Sonnet 5.5, condition A pour
les tâches impaires, condition C pour les paires. Pour chacune, la liste des remarques qu'un relecteur
senior ferait sur le diff, avec fichier et ligne (chemins relatifs à `src/{main,test}/java/io/github/mekkiamiri/ratchet/`,
numéros de ligne de l'arbre `agent`, vérifiables dans [diffs/](diffs/)). Puis chaque remarque est classée :
« vue par une des 11 règles » (une violation est levée sur ce code), « vue par PMD/CPD/SpotBugs » (un
avertissement de la configuration ci-dessus tombe sur ce code et dit la même chose), « vue par personne ».
Champ supplémentaire `regle_voisine` : la règle dont la remarque est cousine (même famille d'erreur, forme non visée).

### 4. Injection de défauts ([injecter.py](injecter.py), [defauts.json](defauts.json))

20 défauts réalistes de 2026 (pas les erreurs du catalogue), écrits avant de lancer la mesure, chacun
comme des remplacements exacts de texte dans une copie produite par l'agent (Sonnet 5.5, condition A,
passage 1). Pour chaque défaut :
- **11 règles** : `compter.py` remet les règles d'origine et lance `ProjectArchTest` + `TestSourcesArchTest`, c'est-à-dire exactement ce que le hook de la condition C lance après chaque fichier ;
- **outils** : PMD/CPD/SpotBugs sur l'arbre avant et après injection ; vu si le nombre d'avertissements d'une règle augmente dans un fichier touché (on compare des comptes, pas des lignes : l'injection décale les lignes et certaines règles signalent la déclaration de la méthode) ;
- **tests** : tous les tests du projet et de l'agent (règles retirées) ; vu si au moins un test devient rouge.

Les injections sont propres (imports mis à jour) pour que les outils ne « voient » pas un import inutilisé à la place du défaut.

## Résultats

### Passages

| Lot | Passages | Nouvelles violations des 11 règles | Tests verts | Coût moyen | Coût total | Durée moyenne |
|---|---|---|---|---|---|---|
| Sonnet 5.5, A rien | 20 | 0 | 20/20 | 0,15 $ | 2,98 $ | 46 s |
| Sonnet 5.5, C règles + hook | 20 | 0 | 20/20 | 0,16 $ | 3,30 $ | 68 s |
| Opus 5.5, A rien | 10 | 0 | 10/10 | 0,41 $ | 4,06 $ | 81 s |

Coût de la campagne : 10,34 $ pour les 50 passages valides, plus 2,52 $ pour les 15 passages invalides.
Durée : 25 minutes (trois lots en parallèle), puis environ 25 minutes d'analyse et 30 minutes d'injection.

### Code ajouté, mesuré par les outils (moyennes par copie)

| | Sonnet A | Sonnet C | Opus A |
|---|---|---|---|
| Copies | 20 | 20 | 10 |
| Lignes ajoutées prod / tests (non vides) | 26,2 / 23,1 | 26,2 / 25,1 | 36,8 / 48,2 |
| Nouveaux types en prod (par copie) | 0,75 | 0,65 | 1,0 |
| Nouvelles interfaces (total) / à une seule implémentation | 0 / 0 | 0 / 0 | **2 / 2** |
| Complexité cyclomatique ajoutée en prod (PMD) | +4,0 | +3,65 | +4,6 |
| Complexité max d'une méthode touchée | 7 | 7 | 5 |
| Duplications CPD touchant le nouveau code (total) | 0 | 0 | 0 |
| Avertissements PMD nouveaux (total) | 0 | 4 | 1 |
| Avertissements SpotBugs nouveaux (total) | 1 | 0 | 7 |
| Tests ajoutés (total) | 49 | 59 | 44 |
| Assertions par test | 1,94 | 1,93 | 2,34 |
| Tests sans assertion | 0 | 0 | 0 |
| Part des tests qui visent null/vide · erreur · frontière | 22 % · 37 % · 22 % | 24 % · 36 % · 32 % | 20 % · 36 % · 48 % |
| Part des tests qui visent au moins un cas limite | 61 % | 68 % | 73 % |
| Couverture JaCoCo des lignes ajoutées | 94,9 % | 96,7 % | 92,6 % |
| Méthodes ajoutées jamais appelées / appelées seulement par les tests (total) | 0 / 4 | 0 / 5 | 0 / 1 |

Lignes ajoutées par tâche (prod/tests, moyenne) :

| Tâche | Sonnet A | Sonnet C | Opus A |
|---|---|---|---|
| T01 remise | 21/22 | 21/22 | 22/32 |
| T02 GET /orders/{id} (existait déjà) | 0/16 | 0/17 | 0/22 |
| T03 date de livraison | 11/8 | 12/13 | 13/26 |
| T04 export CSV | 81/26 | 81/46 | 119/97 |
| T05 annulation | 10/28 | 10/27 | 21/69 |
| T06 notification | 22/15 | 26/14 | 40/33 |
| T07 /stats | 46/36 | 40/20 | 46/70 |
| T08 archivage planifié | 58/14 | 60/22 | 85/50 |
| T09 frais de port | 12/14 | 13/14 | 22/26 |
| T10 tests du total | 0/50 | 0/54 | 0/57 |

Ce que disent les outils, tels quels :
- **A contre C** : aucune différence mesurable sur le code ajouté (mêmes lignes, même complexité, mêmes tests). Les règles ne changent pas la façon dont l'agent écrit du code neuf sur un projet propre ; elles coûtent +50 % de temps (68 s contre 46 s).
- **Sonnet contre Opus** : Opus écrit 40 % de prod et deux fois plus de tests, pour 2,7 fois le prix. Il est le seul à créer des interfaces : deux, chacune à une seule implémentation (`OrderExporter` en T04, `OrderNotifier` en T06, des ports « hexagonaux » avec un seul adaptateur). Ses tests visent plus souvent une frontière (48 % contre 22 %).
- Les avertissements nouveaux sont rares et presque tous sans intérêt pour un relecteur : `GuardLogStatement` (×4, sur des logs SLF4J déjà paramétrés), `NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE` (×4, `Path.getParent()` qui peut être null en théorie), `THROWS_METHOD_THROWS_CLAUSE_BASIC_EXCEPTION` (×4, `throws Exception` sur des méthodes de test), `MethodNamingConventions` (×1, un nom de test avec un tiret bas).
- Aucun test sans assertion, couverture des lignes ajoutées > 92 % : les métriques classiques de qualité des tests sont **toutes au vert**. La revue ci-dessous montre pourtant des oracles faibles : les métriques ne les voient pas non plus.

### Revue simulée : la couverture du harnais

38 remarques sur 10 diffs ([revue.json](revue.json)).

| Vue par | Remarques | Part |
|---|---|---|
| une des 11 règles (= le harnais) | **0** | **0 %** |
| PMD / CPD / SpotBugs | 0 | 0 % |
| personne | 38 | 100 % |

- Sans les 3 remarques de style, il reste 35 remarques de fond, toutes vues par personne.
- 15 des 38 remarques sont **cousines d'une règle** (`regle_voisine`) : même famille d'erreur que R01, R04, R05/R07, R06, R08, R09, R10 ou R11, mais sous une forme que la règle ne vise pas (ex. R09 interdit `java.util.Date` ; le fuseau UTC codé en dur avec `java.time` passe).
- Sur ces 10 copies, les outils ont levé 2 avertissements (`GuardLogStatement` en T04 et T08) qu'aucun relecteur ne ferait : ils ne comptent pas comme remarques.
- Répartition (par la première étiquette de chaque remarque dans revue.json) : tests faibles, dupliqués ou modifiés (9), cas limites (7), exigences réinterprétées ou contrat d'API qui change de sens (4), conception et architecture (3), code mort (2), sécurité et données personnelles (2), concurrence et robustesse (2), temps (1), argent (1), performance (1), gestion d'erreur (1), ressources (1), nommage (1), style (3).

#### Trois remarques réelles « vues par personne »

1. **La date de livraison a un jour d'avance pour les commandes passées après minuit, heure de Paris.**
   `src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:87` (Sonnet 5.5, T03, condition A) :
   `return createdAt.atZone(ZoneOffset.UTC).toLocalDate().plusDays(3);`. Une commande du 30 à 00h30 à
   Paris a une date UTC au 29. Et le test `OrderTest.java:25-26` fige exactement ce cas (`2027-04-29T23:30:00Z`
   → 2 mai) comme comportement attendu. R09 (pas de `Date`/`SimpleDateFormat`) est satisfaite : c'est du
   `java.time` propre, faux au mauvais endroit.
2. **Une commande vide paie 4,90 € de frais de port.**
   `src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:77` (Sonnet 5.5, T09, condition A) :
   `return subtotal().compareTo(FREE_SHIPPING_THRESHOLD) < 0 ? SHIPPING_FEE : BigDecimal.ZERO;`. Sous-total 0
   < 50, donc 4,90 €. Tests verts, frontière 49,99/50,00 bien testée ; le cas vide n'est pas pensé. Dans le
   même diff, l'agent a changé l'attendu de trois tests existants (`ShopApplicationTest.java:31`,
   `OrderServiceTest.java:38`, `OrderControllerTest.java:32`, 3.00 → 7.90) : légitime ici, et invisible pour
   tout le harnais.
3. **L'export CSV met de l'infrastructure dans la couche application et renvoie au client le chemin du fichier sur le serveur.**
   `src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderCsvExporter.java:27,37,42` et
   `src/main/java/io/github/mekkiamiri/ratchet/order/web/ExportResponse.java:4` (Sonnet 5.5, T04, condition C,
   **avec** règles et hook) : écriture disque et `@Value` dans `application`, `IOException` qui remonte au
   contrôleur sans être traduite (500 générique, chemin jamais testé), et `{"file": "orders.csv", ...}`
   dans la réponse. R05/R07 sont des règles de couches, mais elles ne regardent que domaine→web et
   web→stockage : application→système de fichiers passe.

### Injection de défauts : le taux d'attrape du harnais

20 défauts ([defauts.json](defauts.json), résultats bruts [defauts-resultats.jsonl](defauts-resultats.jsonl)).

| # | Défaut injecté | Copie | Règle cousine | 11 règles | PMD / CPD / SpotBugs | Tests existants |
|---|---|---|---|---|---|---|
| D01 | seuil décalé (`>` devient `>=`) | T01-A-1 | - | non | - | **rouges** |
| D02 | calcul monétaire en `double` via `doubleValue()` | T01-A-1 | R08 | non | - | verts |
| D03 | test sans assertion | T01-A-1 | - | non | **PMD UnitTestShouldIncludeAssert** | verts |
| D04 | oracle faible (`exists()` au lieu de la valeur) | T01-A-1 | - | non | - | verts |
| D05 | horloge système au lieu de la date de création | T03-A-1 | R09 | non | - | **rouges** |
| D06 | année de semaine (`YYYY`) dans le format de date | T03-A-1 | R09 | non | **SpotBugs FS_BAD_DATE_FORMAT_FLAG_COMBO** | verts |
| D07 | fuseau du serveur au lieu d'un fuseau fixé | T03-A-1 | R09 | non | - | **rouges** (voir note) |
| D08 | exception avalée avec un log, l'API annonce un succès | T04-A-1 | R01 | non | - | verts |
| D09 | `null` renvoyé au lieu d'une liste vide | T04-A-1 | R03 | non | - | verts |
| D10 | fichier ouvert sans être fermé | T04-A-1 | - | non | **PMD CloseResource, SpotBugs OS_OPEN_STREAM** | verts |
| D11 | méthode dupliquée par copier-coller | T04-A-1 | - | non | **CPD** | verts |
| D12 | transition d'état trop permissive (annulée → expédiée) | T05-A-1 | - | non | - | verts |
| D13 | test qui vérifie le mock au lieu du code | T06-A-1 | - | non | - | verts |
| D14 | liste non thread-safe dans un singleton Spring | T06-A-1 | - | non | - | verts |
| D15 | notification envoyée avant l'enregistrement | T06-A-1 | - | non | (PMD VariableCanBeInlined, hors sujet) | verts |
| D16 | interface + fabrique pour une seule règle | T07-A-1 | - | non | - | verts |
| D17 | `@Transactional` contourné par un appel interne | T08-A-1 | R06 | non | - | verts |
| D18 | expression cron fausse (toutes les heures) | T08-A-1 | - | non | - | verts |
| D19 | test désactivé (`@Disabled`) | T10-A-1 | R11 | non | - | verts |
| D20 | oracle recalculé avec le code testé | T10-A-1 | - | non | - | verts |

| Attrapé par | Défauts | Taux |
|---|---|---|
| les 11 règles (= le harnais, hook compris) | **0** | **0 %** |
| PMD / CPD / SpotBugs (signal pertinent) | 4 | 20 % |
| les tests existants | 3 | 15 % |
| au moins un des trois | 7 | 35 % |
| **personne** | **13** | **65 %** |

- Les 8 défauts cousins d'une règle (D02, D05, D06, D07, D08, D09, D17, D19) : **0 attrapé par les règles**. R08 voit `new BigDecimal(0.1)`, pas `BigDecimal.valueOf(x.doubleValue() * 0.1)` ; R01 voit `catch (Exception e)`, pas `catch (IOException e) { LOG.warn(...) }` ; R06 voit `@Transactional` sur une méthode privée, pas l'appel interne qui contourne le proxy de la même façon ; R11 voit un test mal nommé qui ne tourne jamais, pas un `@Disabled` qui ne tourne jamais non plus.
- Les 5 défauts de test (D03, D04, D13, D19, D20) : un seul vu par un outil (D03, et seulement parce que nous avons activé une règle PMD que quickstart désactive), aucun par les tests (par construction : un test affaibli reste vert).
- D15 : PMD signale `VariableCanBeInlined` sur la ligne modifiée, sans rapport avec le défaut (l'ordre notification/enregistrement) ; compté « vu par personne ».
- Note D07 : le test devient rouge parce que la machine de mesure est à Paris (CET) ; sur une CI en UTC, le même défaut laisse tous les tests verts.

## Limites

- **Revue simulée, pas humaine.** Les 38 remarques ont été écrites par l'agent de code (Opus 5.5) en
  jouant le relecteur senior, une seule fois, sans second relecteur pour mesurer l'accord. Chaque
  remarque cite son fichier et sa ligne pour pouvoir être contestée ; le classement « vue par » est,
  lui, mécanique (une violation ou un avertissement tombe-t-il sur ce code ?). Le chiffre 0 % du
  harnais ne dépend pas du relecteur : aucune règle n'a sonné sur aucune copie.
- **Défauts choisis par le mesureur.** Les 20 défauts sont « réalistes de 2026 » selon notre jugement ;
  un autre jeu donnerait d'autres taux pour les outils et les tests. Le 0 % des règles, lui, tient
  pour tout défaut qui n'est pas une des 11 formes visées.
- **Un petit projet** (414 lignes au départ), des tâches courtes, un seul langage. Les copies de la
  campagne du 22/11 ayant été supprimées, les sorties ont été régénérées le 25/11 avec les mêmes tâches.
- **Outils dans une configuration donnée.** PMD quickstart + une règle, SpotBugs au plus bavard. Error
  Prone n'a pas pu tourner hors ligne (voir plus haut) : il aurait probablement vu D06 (`MisusedWeekYear`),
  déjà vu par SpotBugs : le compte des outils ne changerait pas. Sans PIT, la force des tests n'est mesurée que par
  des heuristiques (assertions, mots-clés) et par l'injection de défauts.
- **Heuristiques de test et de code mort** volontairement simples (mots-clés, recherche de noms) : elles
  peuvent rater un cas limite nommé autrement, ou compter comme « appelée » une méthode homonyme.
- **Échantillon Opus** : 1 passage par tâche (10), contre 2 pour Sonnet.

## Rejouer

```bash
JAVA_HOME=<JDK 25>
python3 mesures/lancer.py --conditions A --passages 2 --modele claude-sonnet-5-5 --garder \
    --dossier-copies /tmp/aveugle-copies/sonnet-A --etiquette=-aveugle-sonnet-A --java-home $JAVA_HOME
# (idem --conditions C ; --modele claude-opus-5-5 --passages 1)
cd mesures/these-a/aveugle
python3 analyser.py --copies sonnet-A=/tmp/aveugle-copies/sonnet-A --copies sonnet-C=... --copies opus-A=... \
    --sortie mesures.jsonl --diffs diffs
python3 injecter.py --defauts defauts.json --copies sonnet-A=/tmp/aveugle-copies/sonnet-A --sortie defauts-resultats.jsonl
python3 resumer.py   # écrit synthese.json
```

Ne pas mettre les copies sous un dossier que l'agent de code protège en écriture (voir passages invalides).

Fichiers : [passages/](passages/) (une ligne par passage, sortie de lancer.py), [mesures.jsonl](mesures.jsonl)
(une ligne par copie, sortie d'analyser.py), [diffs/](diffs/) (le diff de chaque copie, sans le harnais),
[revue.json](revue.json), [defauts.json](defauts.json), [defauts-resultats.jsonl](defauts-resultats.jsonl),
[synthese.json](synthese.json).
