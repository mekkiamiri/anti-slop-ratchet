# Thèse A, mesure 2 : revue croisée de 10 diffs de l'agent (28/11/2026)

Question : quand deux relecteurs indépendants trouvent des défauts dans le code de l'agent, combien
le harnais (les 11 règles + le hook, PMD/SpotBugs, les tests) en voit-il ?

**En une phrase : un agent de revue et un juge à l'aveugle trouvent ensemble 34 défauts différents dans
les 10 diffs (dont 6 majeurs, tous trouvés par les deux) ; le harnais n'en voit aucun : 0 par les règles,
0 par PMD/SpotBugs, 0 par les tests (tous verts).**

Cette mesure remplace la « revue simulée » de [../aveugle/](../aveugle/README.md) (38 remarques écrites par
un seul agent jouant le relecteur), gardée comme historique.

## Protocole

1. **Les mêmes 10 diffs** que l'ancienne revue : passage 1 de Sonnet 5.5, condition A (sans règles) pour
   les tâches impaires, C (règles + hook) pour les paires ([../aveugle/diffs/](../aveugle/diffs/)).
2. **Anonymisation** (méthode du banc spec-driven du Lab : sorties renommées par des lettres avant la
   relecture) : chaque copie devient `diff-A` … `diff-K` (sans I) par tirage à graine fixe (20261128).
   Retirés de chaque arbre : les règles du talk, les mauvais exemples, la configuration de l'agent de code ;
   nom du projet neutralisé. Chaque dossier : l'arbre après le passage, le diff, le ticket mot pour mot.
   La correspondance ([correspondance.json](correspondance.json)) n'a été ouverte qu'après les deux revues.
3. **Deux relecteurs, sans contact entre eux**, lancés en parallèle :
   - (a) **l'agent de revue** `gsd-code-reviewer` (revue « deep » : bugs, sécurité, qualité, tests) →
     [agent-de-revue/REVIEW.md](agent-de-revue/REVIEW.md), [constats.json](agent-de-revue/constats.json) ;
   - (b) **un juge à l'aveugle** (Opus 5.5), avec une grille écrite avant la relecture
     ([grille-juge.md](grille-juge.md) : 5 notes de 1 à 5, défauts pondérés par gravité : critique 5,
     majeure 3, mineure 1, style 0) → [juge-aveugle/jugement.json](juge-aveugle/jugement.json).
   Chaque constat est pointé sur un fichier et des lignes de l'arbre après changement.
4. **Croisement mécanique** ([croiser.py](croiser.py) → [croisement.json](croisement.json)) :
   - deux constats sont le même défaut s'ils portent sur la même copie, le même fichier, à 3 lignes près ;
   - **11 règles et tests** : `harness-mutant` lance le témoin `mvn -o -q verify` sur chaque copie, les
     11 règles remises (exactement ce que lance le hook, plus tous les tests) → [harnais/](harnais/) ;
   - **PMD / CPD / SpotBugs** : les avertissements nouveaux de chaque copie (configuration de
     [../aveugle/](../aveugle/README.md) : PMD quickstart + UnitTestShouldIncludeAssert, CPD 50 jetons,
     SpotBugs effort Max seuil Low), comptés s'ils tombent sur le même fichier à 2 lignes près **et** disent
     la même chose.

## Résultats

### Ce que trouvent les relecteurs

| | Constats | majeurs | mineurs | style |
|---|---|---|---|---|
| (a) agent de revue | 31 | 5 | 21 | 5 |
| (b) juge à l'aveugle | 21 | 3 | 15 | 3 |
| **défauts uniques (a ∪ b)** | **34** | **6** | **24** | **4** |
| trouvés par les deux | 18 | 6 | 10 | 2 |

Aucun constat critique chez l'un ni chez l'autre. **Les 6 défauts majeurs sont trouvés par les deux relecteurs :**

| Copie (lettre) | Défaut majeur | Où |
|---|---|---|
| T03-A (K) | date de livraison calculée sur le jour UTC : un jour trop tôt pour une commande passée entre minuit et 2 h à Paris, et le test fige ce cas | `Order.java:85-88`, `OrderTest.java:25-26` |
| T03-A (K) | le format jj/mm/aaaa n'est vérifié que par `\d{2}/\d{2}/\d{4}` : les deux relecteurs ont remplacé le format par `MM/dd/yyyy` dans une copie, les 20 tests restent verts | `OrderControllerTest.java:33-34` |
| T09-A (B) | une commande vide ou annulée affiche 4,90 € de frais de port ; `total` change de sens dans l'API | `Order.java:75-83` |
| T07-A (A) | `orderCount` compte toutes les commandes, le chiffre d'affaires seulement les confirmées | `OrderService.java:61-68` |
| T04-C (E) | `orders.csv` réécrit sur place sans écriture atomique : deux exports concurrents laissent un fichier mélangé | `OrderCsvExporter.java:37-45` |
| T08-C (J) | une commande archivée répond ensuite 404 sur GET, confirm et cancel ; `findArchivedById` n'est appelé que par les tests | `InMemoryOrderRepository.java:51-57` |

Les deux relecteurs relèvent aussi, chacun de leur côté, que `ship()` (T05) n'est appelé par aucun code de
production. L'agent de revue a retiré `@GetMapping("/{id}")` dans une copie de T02 : le test du 404 reste vert.

### Ce que voit le harnais

| Vu par | Défauts trouvés par la revue | Comment c'est mesuré |
|---|---|---|
| les 11 règles + hook | **0 / 34** | témoin `mvn -o -q verify` vert sur les 10 copies (règles remises) |
| PMD / CPD / SpotBugs | **0 / 34** | 2 avertissements `GuardLogStatement` (T04 l. 43, T08 l. 61) tombent sur les lignes de 4 constats, sans rapport avec eux (garde de niveau de log contre écriture de fichier, transaction) |
| les tests | **0 / 34** | tous verts sur les 10 copies |
| **le harnais (au moins un des trois)** | **0 / 34** | |

### harness-mutant sur les lignes écrites par l'agent

Même harnais (`mvn -o -q verify`, 11 règles + tests), défauts du catalogue de l'outil injectés **uniquement
dans les lignes ajoutées par l'agent** (`--diff` avec le diff de la copie) → [harnais-lignes-agent/](harnais-lignes-agent/).

| Copie | Défauts applicables | Attrapés (par) | Trous |
|---|---|---|---|
| T01-A | 7 | 1 (tests : J01 seuil) | J03 argent en double, J04 arrondi, J20-J23 |
| T02-C | 2 | 0 | J22, J23 |
| T03-A | 6 | 1 (tests : J07 fuseau, voir note) | J08 année de semaine, J20-J23 |
| T04-C | 3 | 0 | J21, J22, J23 (J20 ne compile pas, non compté) |
| T05-A | 5 | 0 | J12 garde retirée, J20-J23 |
| T06-C | 3 | 0 | J14 état exposé, J20, J23 |
| T07-A | 2 | 0 | J22, J23 |
| T08-C | 5 | 1 (tests : J05 horloge) | J15 collection non thread-safe, J18 cron, J21, J23 (J20 ne compile pas) |
| T09-A | 4 | 0 | J20-J23 |
| T10-C | 3 | 0 | J20, J21, J23 |
| **Total** | **40** | **3 (règles 0, tests 3)** | **37 : 30 tests affaiblis, 7 production** |

- Les 11 règles n'attrapent aucun des 40 défauts ; les tests en attrapent 3. Note : J07 (fuseau du serveur)
  n'est attrapé que parce que la machine de mesure est à Paris ; sur une CI en UTC, il passerait.
- 4 des 7 trous de production tombent exactement sur un manque de test signalé par la revue : J04 (arrondi
  jamais testé, T01, les deux relecteurs), J08 (format de date non vérifié, T03, les deux), J12 (refus de
  `ship()` non testé, T05, le juge), J18 (job d'archivage jamais testé, T08, les deux). L'outil les
  retrouve sans relecteur.
- `@Disabled` (J23) passe sur les 10 copies : rien dans ce harnais ne refuse un test désactivé.

### Les notes du juge (révélées après la revue)

| Copie | Lettre | Conformité | Justesse | Tests | Conception | Robustesse | Score de défauts |
|---|---|---|---|---|---|---|---|
| T01-A | C | 4 | 4 | 4 | 5 | 5 | 1 |
| T02-C | G | 4 | 5 | 4 | 5 | 5 | 0 |
| T03-A | K | 4 | 3 | 3 | 5 | 5 | 6 |
| T04-C | E | 4 | 4 | 3 | 3 | 3 | 3 |
| T05-A | D | 4 | 5 | 4 | 4 | 5 | 2 |
| T06-C | F | 5 | 4 | 4 | 5 | 4 | 2 |
| T07-A | A | 4 | 4 | 3 | 4 | 4 | 2 |
| T08-C | J | 4 | 4 | 3 | 4 | 4 | 3 |
| T09-A | B | 4 | 3 | 4 | 3 | 4 | 4 |
| T10-C | H | 5 | 5 | 4 | 4 | 5 | 1 |

Le critère le plus bas est **tests** (moyenne 3,6) : c'est aussi la famille de défauts que le harnais ne voit
jamais (oracles faibles, cas limites non testés). Les conditions A et C portent sur des tâches différentes
(impaires contre paires) : ces notes ne comparent pas A et C.

### Comparaison avec l'ancienne revue simulée (historique)

30 des 34 défauts uniques tombent au même endroit (copie, fichier, lignes à 3 près) qu'une des 38 remarques
de l'ancienne revue simulée. Les deux revues regardent donc les mêmes zones ; la nouvelle s'appuie sur deux
relecteurs indépendants, un juge qui ne connaît pas la condition, et un croisement mécanique.

## Limites

- **Les relecteurs sont des agents, pas des humains.** Ce qui est mécanique : aucune règle n'a sonné,
  aucun test n'est rouge, aucun avertissement d'outil ne dit la même chose qu'un constat. Ce qui dépend des
  relecteurs : la liste des 34 défauts (les 6 majeurs sont confirmés par les deux).
- **Regroupement par position** (même fichier, lignes à 3 près) : deux constats différents sur les mêmes
  lignes comptent pour un, un même défaut décrit à deux endroits compte pour deux.
- **Anonymisation imparfaite** : le diff de T08 touche `ShopApplication.java`, dont le commentaire d'origine
  mentionne « les règles anti-slop » (neutralisé dans l'arbre, pas dans le diff). Il ne dit pas si la copie
  vient de la condition A ou C.
- Un petit projet (414 lignes au départ), 10 diffs, un seul modèle mesuré (Sonnet 5.5).

## Rejouer

```bash
# relecteurs : voir le protocole (dossiers anonymes, grille-juge.md donnée au juge avant la relecture)
python3 croiser.py                       # croisement.json
pip install ../../../outil               # harness-mutant
harness-mutant --projet <copie + règles> --commande "mvn -o -q verify" --exclure '*/ratchet/rules/*' \
    --diff ../aveugle/diffs/<copie>.diff --json harnais-lignes-agent/<copie>.json
```
