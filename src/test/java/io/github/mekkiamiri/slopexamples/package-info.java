/**
 * Code « presque juste » typique d'un agent, rangé ici VOLONTAIREMENT.
 *
 * <p>Chaque sous-paquet {@code rNN} contient {@code bad} (le code qui a valu une remarque de revue)
 * et {@code good} (la correction attendue). Ces classes sont dans les sources de test : la règle
 * appliquée au projet ({@code ProjectArchTest}) ne les voit pas ; {@code AntiSlopRulesTest} les
 * utilise pour prouver que chaque règle attrape le mauvais et laisse passer le bon.
 *
 * <p>Convention : dans {@code bad}, chaque classe dont le nom finit par {@code Slop} doit être signalée.
 */
package io.github.mekkiamiri.slopexamples;
