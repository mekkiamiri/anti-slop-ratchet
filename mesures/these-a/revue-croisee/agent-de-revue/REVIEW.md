---
phase: revue-croisee-10-diffs
reviewed: 2026-11-28T12:10:00Z
depth: deep
files_reviewed: 42
files_reviewed_list:
  - diff-A/src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderService.java
  - diff-A/src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderStats.java
  - diff-A/src/main/java/io/github/mekkiamiri/ratchet/order/domain/OrderRepository.java
  - diff-A/src/main/java/io/github/mekkiamiri/ratchet/order/infrastructure/InMemoryOrderRepository.java
  - diff-A/src/main/java/io/github/mekkiamiri/ratchet/order/web/StatsController.java
  - diff-A/src/main/java/io/github/mekkiamiri/ratchet/order/web/StatsResponse.java
  - diff-A/src/test/java/io/github/mekkiamiri/ratchet/order/web/StatsControllerTest.java
  - diff-B/src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java
  - diff-B/src/test/java/io/github/mekkiamiri/ratchet/ShopApplicationTest.java
  - diff-B/src/test/java/io/github/mekkiamiri/ratchet/order/application/OrderServiceTest.java
  - diff-B/src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTest.java
  - diff-B/src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java
  - diff-C/src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java
  - diff-C/src/main/java/io/github/mekkiamiri/ratchet/order/web/OrderResponse.java
  - diff-C/src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTest.java
  - diff-C/src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java
  - diff-D/src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java
  - diff-D/src/main/java/io/github/mekkiamiri/ratchet/order/domain/OrderStatus.java
  - diff-D/src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTest.java
  - diff-D/src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java
  - diff-E/src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderCsvExporter.java
  - diff-E/src/main/java/io/github/mekkiamiri/ratchet/order/domain/OrderRepository.java
  - diff-E/src/main/java/io/github/mekkiamiri/ratchet/order/infrastructure/InMemoryOrderRepository.java
  - diff-E/src/main/java/io/github/mekkiamiri/ratchet/order/web/ExportResponse.java
  - diff-E/src/main/java/io/github/mekkiamiri/ratchet/order/web/OrderController.java
  - diff-E/src/test/java/io/github/mekkiamiri/ratchet/order/application/OrderCsvExporterTest.java
  - diff-E/src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java
  - diff-F/src/main/java/io/github/mekkiamiri/ratchet/order/application/NotificationService.java
  - diff-F/src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderService.java
  - diff-F/src/test/java/io/github/mekkiamiri/ratchet/order/application/OrderServiceTest.java
  - diff-G/src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java
  - diff-H/src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTotalTest.java
  - diff-J/src/main/java/io/github/mekkiamiri/ratchet/ShopApplication.java
  - diff-J/src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderArchiveJob.java
  - diff-J/src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderService.java
  - diff-J/src/main/java/io/github/mekkiamiri/ratchet/order/domain/OrderRepository.java
  - diff-J/src/main/java/io/github/mekkiamiri/ratchet/order/infrastructure/InMemoryOrderRepository.java
  - diff-J/src/test/java/io/github/mekkiamiri/ratchet/order/application/OrderServiceTest.java
  - diff-K/src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java
  - diff-K/src/main/java/io/github/mekkiamiri/ratchet/order/web/OrderResponse.java
  - diff-K/src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTest.java
  - diff-K/src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java
findings:
  critical: 5
  warning: 21
  info: 5
  total: 31
  necessity: 0
status: issues_found
---

# Revue croisée : 10 changements indépendants (diff-A à diff-K, sans I)

**Relu le :** 2026-11-28
**Profondeur :** deep (lecture de chaque diff, de l'arbre après changement et du ticket ; build et tests ; tests de mutation ciblés)
**Fichiers relus :** les fichiers touchés par chaque diff (liste en en-tête)
**Statut :** issues_found

## Résumé

Les 10 arbres compilent et passent `mvn -o -q test` (dans des copies temporaires, Java 25 / Spring Boot 4.1.2, sortie 0 partout). Aucun constat « critique » (au sens : faux en production pour un cas courant, perte de données, faille). Cinq constats « majeurs » : chacun est faux pour un cas limite plausible ou laisse passer une régression sans qu'un test casse :

- **A** : `orderCount` compte les brouillons et les annulées, alors que `totalRevenue` ne retient que les confirmées. Les deux chiffres ne portent pas sur le même ensemble.
- **E** : l'export réécrit `orders.csv` sur place, sans verrou ni écriture atomique. Deux exports simultanés corrompent le fichier.
- **J** : une commande archivée disparaît de toute l'API (404), et `findArchivedById` n'a aucun appelant en production.
- **K** : la date de livraison est calculée en UTC. Une commande passée entre minuit et 2h, heure de Paris, reçoit une date avec un jour d’avance, et le test fige ce comportement.
- **K** : le format `jj/mm/aaaa` n'est vérifié par aucun test. Une mutation `MM/dd/yyyy` laisse toute la suite verte (vérifié).

Deux tickets (D : endpoint d'annulation, G : GET /orders/{id}) demandaient des endpoints **qui existaient déjà** dans l'arbre de base. Les diffs l'ont vu et ne les ont pas recréés. D ajoute la seule règle manquante (commande expédiée). G n'ajoute que des tests.

**Correspondance des gravités :** CR = majeure (à corriger avant de livrer), WR = mineure, IN = style. Aucune critique.
**Nécessité :** référentiel `necessity-review.md` lu. Aucun constat de nécessité.

**Vérifications dynamiques :**
- Mutation G : avec l'annotation `@GetMapping("/{id}")` retirée, `gettingAnUnknownOrderIsA404` reste vert, parce que la route inconnue répond aussi 404.
- Mutation K : avec le motif `MM/dd/yyyy`, les 20 tests restent verts.

---

## diff-A : GET /stats

### CR-01 : `orderCount` et `totalRevenue` ne portent pas sur le même ensemble de commandes (majeure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderService.java:62-68`
**Problème :** `all.size()` compte toutes les commandes (DRAFT et CANCELLED compris), alors que le chiffre d'affaires filtre sur `CONFIRMED`. Une commande annulée augmente donc le nombre de commandes sans toucher au CA, ce qui fausse tout ratio (panier moyen = CA / nombre). Le ticket parle de « nombre de commandes » et de « chiffre d'affaires total » sans trancher. Le choix n'est exposé que dans la Javadoc, pas dans le contrat JSON (`orderCount`).
**Correctif :** compter le même ensemble que le CA, ou exposer les deux compteurs explicitement :
```java
List<Order> confirmed = all.stream().filter(o -> o.status() == OrderStatus.CONFIRMED).toList();
BigDecimal revenue = confirmed.stream().map(Order::total).reduce(BigDecimal.ZERO, BigDecimal::add);
return new OrderStats(confirmed.size(), revenue); // ou OrderStats(all.size(), confirmed.size(), revenue)
```

### WR-01 : montant comparé en `double` dans le test (mineure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/web/StatsControllerTest.java:31-43`
**Problème :** le CA lu avant l'appel est converti en `double` (l.31), puis comparé à `revenue + 3.0` (l.43). Le contexte Spring est partagé avec les autres classes de test, donc le CA de départ dépend de l'ordre d'exécution. Avec des montants non représentables exactement en binaire (0,10, 0,20…), l'égalité stricte en `double` peut échouer.
**Correctif :** lire en `BigDecimal` (`new BigDecimal(JsonPath.read(...).toString())`) et comparer avec `isEqualByComparingTo`.

### WR-02 : le test ne couvre ni l'exclusion des commandes annulées ni la seconde création (mineure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/web/StatsControllerTest.java:33-43`
**Problème :** aucune commande annulée n'est créée : la règle « annulée exclue du CA » n'est pas testée. Le second `POST /orders` (l.38) n'a aucune assertion : s'il échoue, l'écart sur `orderCount` sera difficile à diagnostiquer.
**Correctif :** ajouter une commande confirmée puis annulée, et affirmer `status().isCreated()` sur chaque création.

---

## diff-B : frais de port

### WR-03 : `total` change de sens dans l'API, sans détail des frais (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:80-83`
**Problème :** `total()` inclut désormais les frais de port, et `OrderResponse` n'expose toujours que `total`. Pour la même commande, la valeur passe de 3.00 à 7.90 sans que le client puisse afficher le sous-total ni les frais.
**Correctif :** ajouter `subtotal` et `shippingFee` à `OrderResponse.from`.

### WR-04 : des frais de port sont facturés sur une commande vide ou annulée, sans test (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:75-78`
**Problème :** `shippingFee()` ne dépend que du sous-total. Une commande sans ligne (sous-total 0) ou annulée affiche `total = 4.90` dans la réponse de `POST /orders/{id}/cancel`. Aucun test ne fixe ce cas.
**Correctif :** renvoyer `BigDecimal.ZERO` quand `lines.isEmpty()` ou `status == CANCELLED`, et le tester.

---

## diff-C : remise de 10 % au-delà de 100 €

### WR-05 : remise arrondie mais pas le sous-total, donc total à plus de 2 décimales (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:77-88`
**Problème :** `OrderRequest.Line.unitPrice` accepte n'importe quelle échelle (pas de `@Digits`). Avec un sous-total de 100.005, la remise vaut 10.00 (`setScale(2, HALF_UP)` de 10.0005) et le total 90.005. Le total renvoyé par l'API n'est alors pas un montant en centimes.
**Correctif :** arrondir aussi `subtotal()`/`total()` à 2 décimales, ou contraindre `unitPrice` avec `@Digits(integer = 10, fraction = 2)`.

### WR-06 : arrondi et seuil juste au-dessus de 100 non testés (mineure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTest.java:22-37`
**Problème :** les tests utilisent 120.00 (remise ronde) et 100.00. Aucun cas où l'arrondi intervient (100.05 donne 10.005, attendu 10.01) ni de cas à 100.01.
**Correctif :** ajouter un test paramétré (100.01 donne 10.00 ; 100.05 donne 10.01 ; 100.04 donne 10.00).

---

## diff-D : annulation impossible après expédition

### WR-07 : `ship()` n'a aucun appelant en production : SHIPPED est inatteignable (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:60-65`
**Problème :** aucun service ni endpoint n'appelle `ship()`. En production, aucune commande ne peut être SHIPPED, donc la nouvelle garde de `cancel()` (l.71-73) ne s'applique jamais. La règle n'est vérifiée qu'en test de domaine, pas en HTTP (pas de test 422 sur une commande expédiée).
**Correctif :** ajouter `OrderService.ship` et `POST /orders/{id}/ship` (avec un test 422 sur l'annulation d'une commande expédiée), ou noter explicitement que l'expédition viendra d'un autre ticket.

### IN-01 : nouvelle valeur d'énumération exposée et insérée au milieu (style)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/domain/OrderStatus.java:6`
**Problème :** `SHIPPED` apparaît dans le champ `status` de l'API (nouvelle valeur pour les clients). L'insérer avant `CANCELLED` décale l'ordinal de celle-ci, ce qui casserait un stockage par ordinal.
**Correctif :** l'ajouter en fin d'énumération et documenter la nouvelle valeur.

---

## diff-E : export CSV

### CR-02 : réécriture de `orders.csv` non atomique et sans verrou (majeure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderCsvExporter.java:37-45`
**Problème :** `Files.write(path, rows, UTF_8)` (l.42) tronque puis réécrit le fichier sur place. Deux `POST /orders/export` simultanés écrivent dans le même fichier en même temps : contenu entrelacé ou tronqué. Un lecteur du fichier pendant l'export voit un fichier partiel.
**Correctif :**
```java
public synchronized int export() throws IOException {
    ...
    Path tmp = Files.createTempFile(path.toAbsolutePath().getParent(), "orders", ".csv.tmp");
    Files.write(tmp, rows, StandardCharsets.UTF_8);
    Files.move(tmp, path, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
```

### WR-08 : fins de ligne de la plateforme alors que la Javadoc annonce RFC 4180 (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderCsvExporter.java:42`
**Problème :** `Files.write(Path, Iterable, Charset)` termine chaque ligne par `System.lineSeparator()`, donc LF sous Linux. RFC 4180 (citée l.57) impose CRLF.
**Correctif :** `Files.writeString(path, String.join("\r\n", rows) + "\r\n", UTF_8)`.

### WR-09 : la réponse divulgue le chemin du fichier sur le serveur (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/web/OrderController.java:35`
**Problème :** `exporter.path().toString()` est renvoyé à un appelant anonyme. Avec un chemin absolu configuré (`orders.export.path`), l'arborescence du serveur est exposée.
**Correctif :** renvoyer seulement le nom du fichier (`path.getFileName()`) ou un identifiant d'export.

### WR-10 : `IOException` remonte en 500 générique (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/web/OrderController.java:33-36`
**Problème :** aucune traduction dans `OrderExceptionHandler`. Une erreur disque produit la page d'erreur par défaut au lieu d'un `ProblemDetail` comme les autres erreurs de l'API.
**Correctif :** ajouter un `@ExceptionHandler(IOException.class)` qui renvoie `ProblemDetail` 500 ou 503 avec un message neutre.

### WR-11 : le test HTTP ne vérifie ni le nombre ni le contenu (mineure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java:51-56`
**Problème :** le test s'appelle `exportAnswersWithTheFileAndTheCount` mais n'affirme que `$.file`. Ni `$.orders` ni le fichier écrit ne sont contrôlés.
**Correctif :** créer une commande, affirmer `$.orders` ≥ 1 et lire `target/test-orders.csv`.

### WR-12 : entrée/sortie fichier dans la couche application (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderCsvExporter.java:17-45`
**Problème :** le projet isole le stockage derrière un port du domaine (`OrderRepository`) avec un adaptateur dans `infrastructure`. L'export écrit directement sur disque depuis `application`, ce qui casse cette séparation.
**Correctif :** garder la mise en forme CSV dans `application` et déplacer l'écriture dans un adaptateur `infrastructure` derrière une interface.

---

## diff-F : notification à la validation

### WR-13 : liste de messages sans borne dans un singleton (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/application/NotificationService.java:15-20`
**Problème :** chaque confirmation ajoute une chaîne à une `CopyOnWriteArrayList` jamais purgée, qui recopie tout le tableau à chaque ajout. Dans une application qui tourne longtemps, la mémoire et le coût de chaque `send` croissent sans limite.
**Correctif :** borner la liste (garder les N derniers messages) ou n'activer ce service qu'en test/démo.

### WR-14 : nom du client écrit dans les journaux à chaque notification (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/application/NotificationService.java:19`
**Problème :** le message construit en `OrderService.java:49` contient `saved.customer()` et il est journalisé en INFO. C'est une donnée personnelle de plus dans les journaux.
**Correctif :** journaliser seulement l'identifiant de commande.

### WR-15 : aucun test de non-envoi quand la validation échoue (mineure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/application/OrderServiceTest.java:43-54`
**Problème :** seul le chemin nominal est testé. Si l'appel à `send` passait avant `save` ou avant `order.confirm()`, aucun test ne casserait.
**Correctif :** tester qu'aucun message n'est envoyé pour une commande vide (exception `InvalidOrderException`) ni après une `ConcurrentOrderUpdateException`.

---

## diff-G : GET /orders/{id}

(L'endpoint et la traduction 404 existaient déjà, `OrderController.java:37-40`. Le diff n'ajoute que des tests.)

### WR-16 : le test 404 passe même sans l'endpoint (mineure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java:63-66`
**Problème :** le test n'affirme que le code 404. Vérifié par mutation : avec `@GetMapping("/{id}")` retiré, la route inconnue répond aussi 404 et le test reste vert. Il ne distingue pas « commande introuvable » de « route absente ».
**Correctif :** affirmer le corps `ProblemDetail` : `jsonPath("$.detail").value("Commande introuvable : absente")`.

### IN-02 : variable `location` qui contient le corps de la réponse (style)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java:52-55`
**Problème :** le nom suggère l'en-tête `Location`. En plus, la création n'est pas vérifiée (`status().isCreated()`) avant la lecture de `$.id`.
**Correctif :** renommer en `created` et ajouter `.andExpect(status().isCreated())`.

---

## diff-H : tests du total

### IN-03 : assertion sensible à l'échelle du `BigDecimal`, contrairement aux autres (style)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTotalTest.java:54`
**Problème :** `isEqualTo(new BigDecimal("0.30"))` échoue si un refactoring renvoie 0.3 ou 0.300, alors que le total est juste. Les 7 autres tests utilisent `isEqualByComparingTo`.
**Correctif :** utiliser `isEqualByComparingTo("0.30")`, ou documenter que l'échelle fait partie du contrat.

### IN-04 : doublon avec `OrderTest` (style)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTotalTest.java:26-31`
**Problème :** `theTotalSumsAllLines` reprend `OrderTest.totalIsTheExactSumOfTheLines` (somme de deux lignes) dans une seconde classe.
**Correctif :** garder une seule version.

### IN-05 : oracle qui se compare à lui-même (style)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTotalTest.java:66-70`
**Problème :** `aCopyKeepsTheSameTotal` compare `copy.total()` à `order.total()` au lieu d'une valeur attendue fixe.
**Correctif :** comparer à `"8.00"`.

---

## diff-J : archivage nocturne

### CR-03 : les commandes archivées disparaissent de l'API (majeure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/infrastructure/InMemoryOrderRepository.java:51-57`
**Problème :** `archiveCreatedBefore` retire les commandes de `orders`. `GET /orders/{id}`, `confirm` et `cancel` répondent alors 404 « Commande introuvable » pour toute commande de plus de 30 jours. `findArchivedById` (`OrderRepository.java:19-20`) n'est appelé que par le test. Le contrat de `GET /orders/{id}` change sans que le ticket le demande.
**Correctif :** faire retomber `OrderService.get` sur `findArchivedById` (lecture seule), ou renvoyer un statut explicite (410 Gone, ou statut ARCHIVED) plutôt que « introuvable ».

### WR-17 : 409 « modifiée entre-temps » trompeur après un archivage (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/infrastructure/InMemoryOrderRepository.java:52-55`
**Problème :** une confirmation qui a lu la commande juste avant l'archivage appelle `save` sur un identifiant absent. `current = 0` est différent de `version = 1`, donc `ConcurrentOrderUpdateException` est levée (« version enregistrée 0 ») et l'API répond 409. Le résultat est sûr (pas de résurrection), mais le message est faux.
**Correctif :** dans `save`, si `stored == null && order.version() > 0` et que l'identifiant est dans `archived`, lever une exception dédiée (commande archivée).

### WR-18 : pas de frontière transactionnelle sur le cas d'usage, alors que le ticket l'exige (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/application/OrderService.java:58-63`
**Problème :** le ticket demande l'archivage « dans une transaction ». L'atomicité repose entièrement sur le `synchronized` de l'adaptateur en mémoire. C'est justifié ici (`spring-tx` n'est qu'en scope test), mais un adaptateur JPA ne pourrait pas tenir le « tout ou rien » du port sans `@Transactional` sur ce cas d'usage, que la Javadoc de la classe (l.18-21) prescrit pourtant.
**Correctif :** noter l'écart dans la Javadoc de `archiveOldOrders`, ou prévoir `@Transactional` dès qu'un stockage transactionnel arrive (règle R06).

### WR-19 : borne des 30 jours et planification non testées (mineure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/application/OrderServiceTest.java:51-67`
**Problème :** le test utilise 31 et 29 jours, sans cas à exactement 30 jours (`isBefore` strict). Rien ne vérifie que `OrderArchiveJob.run` est planifié (cron `0 0 2 * * *`, UTC) ni qu'il appelle le service.
**Correctif :** ajouter un cas à exactement 30 jours (non archivée) et un test d'intégration du job.

---

## diff-K : date de livraison estimée

### CR-04 : date calculée en UTC, donc un jour trop tôt pour les commandes passées après minuit, heure de Paris (majeure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:85-88`
**Problème :** `createdAt.atZone(ZoneOffset.UTC).toLocalDate()`. Une commande passée à 23h30Z le 29/04, soit le 30/04 à 01h30 heure de Paris, reçoit 02/05 au lieu de 03/05. Cela touche chaque commande passée entre minuit et 2h heure de Paris en été (entre minuit et 1h en hiver). Le format `jj/mm/aaaa` du ticket indique un public francophone.
**Correctif :** calculer dans le fuseau métier (`ZoneId.of("Europe/Paris")`, ou le fuseau d'une `Clock`/propriété injectée) :
```java
public LocalDate estimatedDeliveryDate(ZoneId businessZone) {
    return createdAt.atZone(businessZone).toLocalDate().plusDays(3);
}
```

### CR-05 : le format `jj/mm/aaaa` n'est protégé par aucun test (majeure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java:33-34`
**Problème :** le test ne vérifie que le motif `\d{2}/\d{2}/\d{4}`. Vérifié par mutation : avec le motif `MM/dd/yyyy` dans `OrderResponse`, les 20 tests restent verts. L'exigence explicite du ticket n'est donc pas protégée.
**Correctif :** utiliser une `Clock` fixe dans le test ou calculer la valeur attendue (`LocalDate.now(clock).plusDays(3).format(ofPattern("dd/MM/yyyy"))`), et ajouter un test unitaire de `OrderResponse.from` avec une date dont le jour est supérieur à 12.

### WR-20 : le test fige l'interprétation UTC (mineure)
**Fichier :** `src/test/java/io/github/mekkiamiri/ratchet/order/domain/OrderTest.java:25-26`
**Problème :** le cas « fin de mois » (23h30Z le 29/04, attendu 02/05) est précisément le cas où UTC et Paris divergent. Le test verrouille le comportement de CR-04 au lieu de le révéler.
**Correctif :** attendre 03/05 pour un fuseau Europe/Paris une fois CR-04 corrigé.

### WR-21 : fuseau codé en dur dans le domaine, au lieu de celui de l'horloge (mineure)
**Fichier :** `src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:87`
**Problème :** l'application centralise le temps dans le bean `Clock` (`ClockConfiguration`). `ZoneOffset.UTC` en dur ignore ce point unique. Changer le fuseau de l'horloge ne changerait pas la date de livraison.
**Correctif :** passer le fuseau (ou la `Clock`) en paramètre depuis le service ou la couche web.

---

_Relu le : 2026-11-28T12:10:00Z_
_Relecteur : gsd-code-reviewer_
_Profondeur : deep_
