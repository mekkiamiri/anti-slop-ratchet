# Proposition (français)

**Format :** Tools-in-Action (30 min) · **Track :** Méthodologie et pratiques de développement (pas le track IA, où le sujet serait un parmi trente) · **Niveau :** intermédiaire · **Langue :** français

## Titre (41 caractères)

Mon harnais était aveugle, pas mon agent

## Abstract

Vous avez mis votre agent de code dans un harnais : tests, linters, règles ArchUnit, un hook qui le bloque tant que c'est rouge. Le mien n'a jamais sonné en 180 tâches. Bon signe ? Personne ne le sait : on mesure la couverture de ses tests, jamais celle de son harnais.

Je l'ai mesurée. L'agent ne triche pas : 0 contournement sur 144 tickets qui exigent ce qu'une règle interdit. Mais deux relecteurs (un agent de revue et un juge à l'aveugle) trouvent 34 défauts dans 10 de ses diffs, et mon harnais n'en voit aucun ; sur 20 défauts injectés, mes règles n'en attrapent aucun.

J'en ai fait un outil open source, harness-mutant : une commande injecte des défauts réalistes dans une copie de votre projet, lance votre harnais et répond « il attrape 7 défauts sur 13 ; voici les trous, et ce qui fermerait chacun ».

Vous repartirez avec : l'outil et son catalogue de défauts à étendre ; la méthode pour fermer un trou et suivre le score en CI ; deux garde-fous gratuits, le droit d'abandonner pour l'agent (coût ÷ 2,2) et le diff vide refusé.

## Notes au comité

```
Pourquoi ce n'est pas « encore un talk ArchUnit pour le code d'IA » :
- Ce talk-là a déjà été donné (Devoxx BE 2026). Ici les règles tiennent en une slide :
  le sujet est la mesure du harnais lui-même, la question que Böckeler laisse ouverte
  (« We need a way to evaluate harness coverage … similar to what code coverage and
  mutation testing do for tests », martinfowler.com, 2 avril 2026).
- Le talk rapporte un résultat contre ma propre attente : je pensais que l'agent
  contournerait les règles (comme ImpossibleBench le montre pour les tests) ; il ne l'a
  jamais fait en 144 passages. Le vrai trou était ailleurs : les règles regardent les
  erreurs d'hier.

Pourquoi moi :
- Tech Lead et architecte système, référent IA d'un centre de développement logiciel ;
  18 ans de software craftsmanship (DDD, TDD, BDD).
- Contributions proposées : Google ADK Java (PR #1383, #1300, #653), Spring AI A2A
  (PR #13, #15), AG-UI (PR #923).

Ce qui tourne déjà :
- Dépôt : github.com/mekkiamiri/anti-slop-ratchet, CI GitHub Actions (mvn verify).
  Sans modèle : python3 mesures/test_compter.py ; python3 mesures/lancer.py --essai-a-blanc
- L'outil harness-mutant (outil/, Python bibliothèque standard, 16 tests en CI) :
  harness-mutant --projet . --commande "mvn -o -q verify" ; sorties réelles dans outil/exemples/.
- Trois campagnes de novembre 2026 (180, 144 et 50 passages d'agent), JSONL bruts,
  classifieur, injecteur de défauts, commandes pour tout rejouer ; 31 passages relus à la main ;
  revue croisée de 10 diffs (agent de revue + juge à l'aveugle, grille écrite avant).
- Slides en ligne : mekkiamiri.github.io/anti-slop-ratchet/slides/
- Démo live : harness-mutant sur le projet du talk (1 min 43), puis un patch d'une règle et
  deux tests qui fait passer le score de 7 à 10 sur 13. Plan B : sorties enregistrées.

Limites dites sur scène :
- un petit projet Java (414 lignes), deux modèles (novembre 2026), deux relecteurs qui sont
  des agents et non des humains, un catalogue de défauts écrit par moi.
  Ce qui ne dépend pas de ces choix : aucune règle n'a sonné sur les 50 copies, et aucune
  n'a vu les 8 défauts cousins directs d'une règle.

Plan minuté (30 min), en 4 étapes :
- 0-5      Départ : votre harnais (tests, linters, ArchUnit, hook) ; 180 tâches, rien ne sonne
- 5-14     Problème : un harnais muet ne dit rien ; l'agent ne triche pas (0/144) ;
           revue croisée : 34 défauts, 0 vu par le harnais ; 20 défauts injectés, 0 vu
- 14-15:30 Cible : la couverture du harnais, comme celle des tests
- 15:30-30 Comment : harness-mutant en démo, sur le code de l'agent, fermer 3 trous ;
           trois gestes ; limites et dépôt

Expérience de scène :
- [À compléter par Mekki : meetups, JUG, présentations internes (nombre de participants), lien vidéo]

Accord employeur : [à compléter par Mekki]
Adaptable : Quickie 20 min (10 slides : le chemin et la démo de l'outil).
```

## Bio (3e personne, 364 caractères)

Mekki Amiri est Tech Lead et architecte système, référent IA d'un centre de développement logiciel. Il pratique le software craftsmanship depuis 18 ans (DDD, TDD, BDD) et passe désormais son temps à mesurer ce que les agents de code font vraiment, plutôt que ce qu'on craint qu'ils fassent. Il a proposé des contributions à Google ADK Java, Spring AI A2A et AG-UI.
