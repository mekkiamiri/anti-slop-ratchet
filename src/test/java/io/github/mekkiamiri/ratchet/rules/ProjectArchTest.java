package io.github.mekkiamiri.ratchet.rules;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.junit.ArchTests;

/**
 * Tout le catalogue appliqué au code de production : chaque champ {@code @ArchTest} de
 * {@link AntiSlopRules} est repris automatiquement. C'est ce test que lancent le hook de l'agent
 * ({@code mvn -q test -Dtest='*ArchTest'}) et la CI.
 */
@AnalyzeClasses(packages = "io.github.mekkiamiri.ratchet", importOptions = ImportOption.DoNotIncludeTests.class)
class ProjectArchTest {

    @ArchTest
    static final ArchTests ALL_RULES = ArchTests.in(AntiSlopRules.class);
}
