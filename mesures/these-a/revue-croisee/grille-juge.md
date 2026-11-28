# Grille du juge à l'aveugle (écrite le 28/11/2026, avant toute relecture)

Méthode reprise du banc spec-driven du Lab (version publique : `lab/benchmarks`) : les sorties sont
renommées par des lettres avant la relecture, le juge ne sait pas quelle condition les a produites,
la grille est fixée avant, les défauts sont pondérés par gravité.

## Anonymisation

- 10 diffs (ceux de l'ancienne revue simulée : passage 1 de Sonnet 5.5, condition A pour les tâches
  impaires, C pour les paires) ; chacun renommé `diff-A` … `diff-K` (sans I) par un tirage au sort à
  graine fixe (20261128). La correspondance reste hors du dossier relu jusqu'à la fin des deux revues.
- Retirés de chaque arbre : les règles du talk (`rules/`), les mauvais exemples (`slopexamples/`), la
  configuration de l'agent de code, la doc du talk ; le nom du projet est neutralisé (`shop-demo`).
- Chaque dossier contient : l'arbre complet après le passage, `CHANGEMENT.diff` (le diff de l'agent)
  et `TICKET.txt` (le ticket donné à l'agent, mot pour mot).

## Notes par diff (1 à 5)

| Critère | 5 | 3 | 1 |
|---|---|---|---|
| Conformité au ticket | fait exactement ce qui est demandé, rien d'autre | interprète un point sans le dire | à côté du ticket |
| Justesse | cas limites (vide, frontière, null, fuseau, arrondi) traités | un cas limite raté | faux sur le cas nominal |
| Tests | oracles précis, cas limites testés, un test rouge si le code casse | oracles partiels | tests qui restent verts quoi qu'il arrive |
| Conception | simple, dans la bonne couche, cohérente avec le projet | une entorse (couche, abstraction inutile) | structure qui gêne la suite |
| Robustesse et sécurité | erreurs traduites, ressources fermées, aucune fuite d'info | un point faible | défaut exploitable ou perte de données |

## Défauts

Chaque défaut : diff, fichier, ligne(s), gravité, catégorie, une phrase vérifiable.

| Gravité | Poids | Sens |
|---|---|---|
| critique | 5 | faux en production pour un cas courant, perte de données, faille |
| majeure | 3 | faux pour un cas limite plausible, contrat d'API qui change, test qui ne protège pas |
| mineure | 1 | dette, lisibilité, test incomplet sans risque immédiat |
| style | 0 | goût, cohérence de forme |

Score de défauts d'un diff = somme des poids. Le juge ne connaît ni les règles du talk ni les outils
qui seront croisés ensuite.
