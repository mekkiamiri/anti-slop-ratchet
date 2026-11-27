# Proposition (français)

**Format :** Tools-in-Action (30 min) · **Track :** Méthodologie et pratiques de développement (pas le track IA, où le sujet serait un parmi trente) · **Niveau :** intermédiaire · **Langue :** français

## Titre (41 caractères)

Mon harnais était aveugle, pas mon agent

## Abstract

J'ai changé 11 remarques de revue récurrentes en règles qui bloquent mon agent de code : c'est son harnais. Sur 180 tâches ordinaires, elles n'ont jamais sonné. Code propre ou capteurs aveugles ? Birgitta Böckeler pose la question et la laisse ouverte.

J'ai mesuré les deux réponses. L'agent triche-t-il ? 12 tickets qui exigent ce qu'une règle interdit, 144 passages, deux modèles : aucun contournement, il cite la règle et vous rend la décision. Les règles sont-elles aveugles ? Sur 20 défauts réalistes injectés dans son code, elles n'en voient aucun, PMD et SpotBugs 4, les tests 3 : 13 passent sans bruit.

Vous repartirez avec : une méthode pour mesurer votre harnais en y injectant des défauts, comme le mutation testing le fait pour les tests ; une phrase qui donne à l'agent le droit d'abandonner (coût ÷ 2,2) ; un contrôle qui refuse le diff vide. Tout est dans un dépôt public, données brutes comprises.

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
- Trois campagnes de novembre 2026 (180, 144 et 50 passages d'agent), JSONL bruts,
  classifieur, injecteur de défauts, commandes pour tout rejouer ; 31 passages relus à la main.
- Slides en ligne : mekkiamiri.github.io/anti-slop-ratchet/slides/
- Démo live : la vraie transcription de l'agent qui plaide, puis un défaut injecté en direct
  avec injecter.py sur une copie reconstruite depuis le diff publié (git apply).
  Plan B : vidéo enregistrée.

Limites dites sur scène :
- un petit projet Java (414 lignes), deux modèles (novembre 2026), une revue jouée par un
  agent et non par un humain, 20 défauts choisis par moi hors des 11 formes visées.
  Ce qui ne dépend pas de ces choix : aucune règle n'a sonné sur les 50 copies, et aucune
  n'a vu les 8 défauts cousins directs d'une règle.

Plan minuté (30 min) :
- 0-4      le harnais et la question de Böckeler (une règle, le hook)
- 4-5:30   sur 180 tâches, aucune règle ne sonne : qualité ou cécité ?
- 5:30-14:30  hypothèse 1, l'agent triche : 12 tickets, 144 passages, 0 contournement,
              l'agent plaide, le droit d'abandon (démo : la transcription)
- 14:30-25    hypothèse 2, les règles regardent ailleurs : 20 défauts injectés, 0 vu
              par les règles, un vrai défaut de fuseau (démo : injection en direct)
- 25-30    trois gestes, limites, dépôt

Expérience de scène :
- [À compléter par Mekki : meetups, JUG, présentations internes (nombre de participants), lien vidéo]

Accord employeur : [à compléter par Mekki]
Adaptable : Quickie 15 min possible (hypothèse 2 seule : injection de défauts et diff vide).
```

## Bio (3e personne, 364 caractères)

Mekki Amiri est Tech Lead et architecte système, référent IA d'un centre de développement logiciel. Il pratique le software craftsmanship depuis 18 ans (DDD, TDD, BDD) et passe désormais son temps à mesurer ce que les agents de code font vraiment, plutôt que ce qu'on craint qu'ils fassent. Il a proposé des contributions à Google ADK Java, Spring AI A2A et AG-UI.
