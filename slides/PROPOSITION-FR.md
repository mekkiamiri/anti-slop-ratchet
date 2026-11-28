# Proposition (français)

**Format :** Tools-in-Action (30 min) · **Track :** Méthodologie et pratiques de développement (pas le track IA, où le sujet serait un parmi trente) · **Niveau :** intermédiaire · **Langue :** français

## Titre (56 caractères)

Votre agent suit vos règles. Que laissent-elles passer ?

## Abstract

Vous encadrez votre agent de code avec un harnais : règles ArchUnit, tests, linters, un hook qui le renvoie corriger tant que c'est rouge. Ça marche : sur 144 tickets qui exigent ce qu'une règle interdit, mon agent n'a jamais contourné une règle ; il corrige son code ou demande à l'humain. Et sur 180 tâches ordinaires, aucune règle n'a échoué. Bon signe ? On mesure la couverture de ses tests, jamais ce que son harnais attrape.

Je l'ai mesuré. Deux relecteurs (un agent de revue et un juge qui ne sait pas si le code a été écrit avec ou sans règles) trouvent 34 défauts dans 10 diffs de l'agent, comme une date de livraison calculée en UTC, un jour trop tôt pour un client à Paris ; ni règle, ni linter, ni test ne les signale. Ce n'est pas que le harnais est mauvais : il ne voit que ce qu'il vise.

Ce talk ne vous dira pas de jeter vos règles. Il vous montre comment mesurer ce qu'elles laissent passer, avec un outil open source, harness-mutant : une commande casse une copie de votre projet, un défaut réaliste à la fois, lance votre build et répond « il attrape 7 défauts sur 13 ; voici les trous, et la règle ou le test qui fermerait chacun ». Une règle ArchUnit et deux tests plus tard : 10 sur 13.

Vous repartirez avec : l'outil et son catalogue de défauts à étendre ; la méthode pour fermer un trou et suivre le score en CI ; deux garde-fous gratuits, autoriser l'agent à s'arrêter et expliquer (coût ÷ 2,2) et ne pas valider un diff vide.

## Notes au comité

```
Pourquoi ce n'est pas « encore un talk ArchUnit pour le code d'IA » :
- Ce talk-là a déjà été donné (Devoxx BE 2026). Ici les règles tiennent en une slide :
  le sujet est la mesure de ce que le harnais attrape, la question que Böckeler laisse ouverte
  (« We need a way to evaluate harness coverage … similar to what code coverage and
  mutation testing do for tests », martinfowler.com, 2 avril 2026).
- Le talk rapporte un résultat contre ma propre attente : je pensais que l'agent
  contournerait les règles (comme ImpossibleBench le montre pour les tests) ; il ne l'a
  jamais fait en 144 passages. Les règles font leur travail ; le trou était ailleurs :
  elles ne voient que ce qu'elles visent, et personne ne mesurait le reste.

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
  Ce qui ne dépend pas de ces choix : aucune règle n'a échoué sur les 50 copies, et aucune
  n'a vu les 8 défauts cousins directs d'une règle.

Plan minuté (30 min, 15 slides), en 4 étapes :
- 0-9      Départ : trois mots (agent de code, harnais, linter) ; une règle ArchUnit et son
           message d'échec ; le hook qui renvoie l'agent corriger (0 contournement sur 144) ;
           180 tâches ordinaires, aucune règle n'échoue, dette nettoyée 30/30
- 9-17     Problème : un harnais qui n'échoue jamais ne dit pas ce qu'il laisse passer ;
           revue croisée : 34 défauts, 0 signalé ; le défaut UTC ; 20 défauts injectés, 13 passent
- 17-19:30 Cible : ce que ce talk ne dit pas (« jetez vos règles ») ; la couverture du
           harnais, comme celle des tests
- 19:30-30 Comment : harness-mutant en démo, une règle et deux tests (7 → 10 sur 13) ;
           trois gestes ; limites et dépôt

Ce que le talk ne dit pas (une slide dédiée) : les règles, ArchUnit, les linters et les
tests ne sont pas inutiles ; ils encadrent l'agent et attrapent ce qu'ils visent. Le message :
mesurez ce qu'ils laissent passer, et fermez les trous.

Expérience de scène :
- [À compléter par Mekki : meetups, JUG, présentations internes (nombre de participants), lien vidéo]

Accord employeur : [à compléter par Mekki]
Adaptable : Quickie 20 min (10 slides : le chemin, les captures et la démo de l'outil).
```

## Bio (3e personne, 364 caractères)

Mekki Amiri est Tech Lead et architecte système, référent IA d'un centre de développement logiciel. Il pratique le software craftsmanship depuis 18 ans (DDD, TDD, BDD) et passe désormais son temps à mesurer ce que les agents de code font vraiment, plutôt que ce qu'on craint qu'ils fassent. Il a proposé des contributions à Google ADK Java, Spring AI A2A et AG-UI.
