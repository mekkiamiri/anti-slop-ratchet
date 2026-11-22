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

État au 22/11/2026 : banc prêt, essai à blanc juste (le faux agent laisse 1 violation R08 et 1 R04, comptées 1 et 1 ;
19 tests fonctionnels verts). **Aucun passage avec un vrai modèle pour l'instant.**

Limites connues : la réussite d'une tâche n'est pas vérifiée par un test caché (seulement « ça compile et les tests passent ») ;
un échantillon de diffs sera relu à la main. ArchUnit ne voit pas tout (voir RATCHET.md, « Ce qu'une règle ne voit pas »).
