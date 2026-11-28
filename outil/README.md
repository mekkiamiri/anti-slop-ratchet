# harness-mutant

**Votre harnais attrape-t-il les défauts de votre agent de code ? Mesurez-le comme vous mesurez vos tests.**

Vous avez mis autour de votre agent de code des règles (ArchUnit, PMD, SpotBugs, Checkstyle), des tests
et un hook qui bloque tant que c'est rouge. Si rien ne sonne jamais, deux explications sont possibles :
le code est bon, ou vos capteurs ne regardent pas au bon endroit. `harness-mutant` tranche : il injecte
un par un des défauts réalistes dans une **copie** de votre projet, lance votre harnais (une commande :
vert = code de sortie 0) et compte ce qu'il attrape. Vous obtenez un score et la liste des trous, avec
pour chacun l'outil ou le test qui l'attraperait.

C'est l'idée du mutation testing ([PIT](https://pitest.org/)), appliquée au harnais entier au lieu des
seuls tests, avec des défauts d'agents de 2026 au lieu de mutations d'opérateurs.

## Trois commandes

```bash
pip install ./outil                      # Python 3.10+, aucune dépendance
harness-mutant --projet . --commande "mvn -o -q verify" --lister   # où chaque défaut s'appliquerait
harness-mutant --projet . --commande "mvn -o -q verify" --json harnais.json
```

Sans installation : `PYTHONPATH=outil python3 -m harness_mutant --projet . --commande "mvn -o -q verify"`.

## Sortie réelle, sur le projet de ce dépôt (28/11/2026, 1 min 43 s)

Harnais du talk : les 11 règles ArchUnit et tous les tests (`mvn -o -q verify`). Les règles elles-mêmes
et leurs mauvais exemples sont exclus de l'injection par le fichier [`.harness-mutant.json`](../.harness-mutant.json)
du dépôt (`{"exclure": ["*/slopexamples/*", "*/ratchet/rules/*"]}`).

```text
Votre harnais attrape 7 défauts sur 13 (54 %).
  attrapés par : tests 7

Les 6 trous (le défaut est entré, la commande est restée verte) :
  J13  contrôle de null retiré  (src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:30)
        pour l'attraper : un test qui construit l'objet avec null
  J14  état interne exposé (copie défensive retirée)  (src/main/java/io/github/mekkiamiri/ratchet/order/domain/Order.java:84)
        pour l'attraper : SpotBugs EI_EXPOSE_REP ; un test qui modifie la liste renvoyée
  J20  assertion supprimée dans un test  (src/test/java/io/github/mekkiamiri/ratchet/ShopApplicationTest.java:29)
  J21  oracle affaibli (isEqualTo devient isNotNull)  (src/test/java/io/github/mekkiamiri/ratchet/ShopApplicationTest.java:30)
  J22  oracle JSON affaibli (value devient exists)  (src/test/java/io/github/mekkiamiri/ratchet/order/web/OrderControllerTest.java:32)
  J23  test désactivé (@Disabled)  (src/test/java/io/github/mekkiamiri/ratchet/ShopApplicationTest.java:22)
```

Les 11 règles n'attrapent aucun des 13 défauts : tout ce qui est attrapé l'est par les tests.
Sortie complète : [exemples/sortie-projet-du-talk.txt](exemples/sortie-projet-du-talk.txt) et [.json](exemples/sortie-projet-du-talk.json).

## Ce que fait l'outil, dans l'ordre

1. Copie le projet dans un dossier temporaire (sans `target/`, `build/`, `.git/`) : votre arbre n'est jamais modifié.
2. **Témoin** : lance la commande sur la copie intacte. Si elle est rouge, l'outil s'arrête (code 2) : un harnais rouge ne mesure rien.
3. Pour chaque défaut du catalogue : le premier endroit où son motif s'applique (ordre stable : fichier, puis position) ; le défaut est écrit, la commande lancée, le fichier remis.
   - code de sortie ≠ 0 : **attrapé**, avec qui a sonné (ArchUnit, PMD, CPD, SpotBugs, Checkstyle, Error Prone, PIT, tests), lu dans la sortie ;
   - code 0 : **trou** ;
   - le défaut ne compile pas à cet endroit : on essaie l'endroit suivant (3 au plus), sinon il n'est pas compté (comme les mutants non viables de PIT) ;
   - motif absent du projet : **non applicable**, pas compté.
4. Score = attrapés / (attrapés + trous).
   Options utiles : `--base main` (ou `--diff fichier.diff`) ne vise que les lignes changées, par exemple le
   code que l'agent vient d'écrire ; `.harness-mutant.json` à la racine du projet fixe les exclusions et
   catalogues par défaut ; `--seuil 60` rend le code de sortie 1 sous 60 % : de quoi en faire un cliquet en CI.

## Le catalogue de défauts (extensible)

[harness_mutant/defauts/java.json](harness_mutant/defauts/java.json) : 23 défauts Java que l'on voit dans
les diffs d'agents (frontières, argent en `double`, horloge et fuseau, exceptions avalées, `null` au lieu
de vide, ressources, gardes retirées, état exposé, concurrence, `@Valid`, codes HTTP, cron, `==`,
et 4 façons d'affaiblir un test). Chaque défaut dit pourquoi il est réaliste et ce qui l'attraperait.

Ajoutez les vôtres dans un fichier au même format et passez-le avec `--defauts` (répétable) :

```json
{"defauts": [{
  "id": "M01", "nom": "montant arrondi à l'euro", "famille": "argent",
  "fichiers": ["src/main/java/**/*.java"],
  "chercher": "setScale\\(2,", "remplacer": "setScale(0,",
  "pourquoi": "les centimes disparaissent des factures",
  "pour_l_attraper": "un test avec un montant à centimes"
}]}
```

Forme exacte aussi acceptée (`remplacements` : `fichier` / `avant` / `apres`), celle du banc du talk :
`--defauts mesures/these-a/aveugle/defauts.json` rejoue les 20 défauts de la mesure du 25/11.

## Briques open source sur lesquelles il s'appuie

L'outil n'analyse rien lui-même : il fait sonner les outils que vous avez déjà, et vous dit lesquels ajouter.

- [PIT](https://pitest.org/) : le mutation testing pour Java ; l'idée, et l'outil à ajouter pour les trous de tests (J20-J22).
- [ArchUnit](https://www.archunit.org/) : les règles d'architecture du harnais du talk ; plusieurs trous se ferment par une règle de 3 lignes (`now()` sans `Clock`, `@Disabled`, `BigDecimal.doubleValue()`).
- [PMD](https://pmd.github.io/) et [SpotBugs](https://spotbugs.github.io/) : ce qu'ils voient est reconnu dans la sortie (ex. `CloseResource`, `EI_EXPOSE_REP`, `FS_BAD_DATE_FORMAT_FLAG_COMBO`).
- [Maven](https://maven.apache.org/) ou n'importe quel outil de build : seule compte la commande et son code de sortie.

## Limites

- Les défauts sont des remplacements de texte (expressions régulières), pas une analyse de l'arbre syntaxique : un motif peut rater une forme écrite autrement. `--lister` montre exactement où chaque défaut tombera.
- Un défaut par exécution, au premier endroit qui compile : c'est un échantillon, pas une couverture exhaustive comme PIT.
- La commande est relancée en entier à chaque défaut : sur un gros module, gardez une commande ciblée (ex. `mvn -o -q verify -pl mon-module`).
- Le catalogue est écrit à la main par l'auteur du talk : un autre jeu de défauts donnerait un autre score. Comparez votre score à lui-même dans le temps, pas à celui d'un autre projet.

## Tests

```bash
python3 -m unittest discover -s outil/tests
```

Licence : Apache-2.0 (voir [LICENSE](../LICENSE)).
