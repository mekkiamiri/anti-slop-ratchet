# Mesure : un prompt se suggère, une règle s'impose

Question : quand un agent de code fait des tâches ordinaires sur ce projet, combien d'erreurs du catalogue
laisse-t-il dans le code rendu, selon qu'il a :

| Condition | Ce que l'agent a |
|---|---|
| **A** rien | le projet seul (ni règles, ni hook, ni consignes) |
| **B** consignes | les 11 remarques de revue écrites dans `CLAUDE.md` ([consignes-CLAUDE.md](consignes-CLAUDE.md)) |
| **C** règles | les règles ArchUnit et le hook qui les lance après chaque fichier et avant de rendre la main |

- 10 tâches écrites **avant** toute mesure, formulées comme des tickets, sans indice : [taches.json](taches.json).
- Après chaque passage, [compter.py](compter.py) remet les règles d'origine et compte les violations par règle, puis lance les tests fonctionnels (ceux du projet et ceux écrits par l'agent).
- Chaque passage part d'une copie neutre du projet (sans README, RATCHET.md, docs ni slides : l'agent ne voit pas le talk).
- Une ligne JSON par passage dans `resultats/` : violations par règle, tests, durée, coût, modèle réellement servi.

```bash
python3 mesures/test_compter.py                 # tests du compteur
python3 mesures/lancer.py --essai-a-blanc       # sans modèle : un faux agent écrit une violation connue
python3 mesures/lancer.py --conditions A,B,C --passages 3 --java-home <JDK 21+>
```

## Résultats du 22/11/2026 (180 passages valides, modèle servi : claude-sonnet-5-5)

Deux projets : **propre** (le projet du dépôt) et **sale** (le même, avec 11 erreurs du catalogue déjà présentes dans le service et le contrôleur : [projet-sale/](projet-sale/)). 10 tâches × 3 conditions × 3 passages par projet. Données brutes : `resultats/2026-11-22.jsonl` (propre), `resultats/2026-11-22-sale.jsonl` (sale), synthèse : `resultats/synthese-2026-11-22.json`.

| Projet | Condition | Nouvelles erreurs | Erreurs à la fin (moyenne) | Tests verts | Coût moyen | Durée moyenne |
|---|---|---|---|---|---|---|
| propre | A rien | 0 | 0 | 30/30 | 0,144 $ | 38 s |
| propre | B consignes | 0 | 0 | 30/30 | 0,140 $ | 37 s |
| propre | C règles + hook | 0 | 0 | 30/30 | 0,183 $ | 59 s |
| sale | A rien | 0 | 11 | 30/30 | 0,163 $ | 46 s |
| sale | B consignes | 0 | 10,2 | 30/30 | 0,156 $ | 40 s |
| sale | C règles + hook | 0 | **0 (30 fois sur 30)** | 30/30 | 0,259 $ | 87 s |

Ce que ça dit :
1. **L'agent ne fait aucune des 11 erreurs**, même sans consignes, même sur un projet qui en contient déjà : il n'imite pas le mauvais code.
2. **Les consignes écrites ne nettoient presque rien** (11 → 10,2 en moyenne).
3. **Les règles branchées font nettoyer toute la dette existante à chaque tâche**, tests toujours verts, pour +59 % de coût et ×1,9 de temps. Sur un vrai legacy (des milliers de violations), ce serait ingérable sans geler l'existant (`FreezingArchRule`) : c'est le choix « geler ou rembourser ».

Contrôles : le compteur détecte une violation injectée à la main dans une copie produite par l'agent (R08 = 1) ; 49 passages ratés pour cause d'accès au modèle (identifiants expirés, coupure du proxy) ont été écartés et relancés (`resultats/2026-11-22-sale-invalides.jsonl`).

Passages de démo (hors campagne, non comptés ci-dessus) : `resultats/demo-2026-11-23.jsonl`, deux passages relancés le 23/11/2026 avec `--garder` pour montrer de vrais diffs dans les slides (propre T01 condition A, sale T06 condition C).

Limites : un seul modèle (le seul servi sur le poste de mesure) ; un petit projet (414 lignes) ; la réussite fonctionnelle de chaque tâche n'est vérifiée que par « compile et tests verts » ; les commentaires du projet propre énoncent certaines règles (biais possible, absent du projet sale).
