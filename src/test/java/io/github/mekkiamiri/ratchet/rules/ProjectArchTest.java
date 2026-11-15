package io.github.mekkiamiri.ratchet.rules;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

/**
 * Le catalogue appliqué au code de production. C'est ce test que lancent le hook de l'agent
 * ({@code mvn -q test -Dtest='*ArchTest'}) et la CI.
 */
@AnalyzeClasses(packages = "io.github.mekkiamiri.ratchet", importOptions = ImportOption.DoNotIncludeTests.class)
class ProjectArchTest {

    @ArchTest
    static final ArchRule r01 = AntiSlopRules.R01_NO_GENERIC_CATCH;
    @ArchTest
    static final ArchRule r02 = AntiSlopRules.R02_NO_FIELD_INJECTION;
    @ArchTest
    static final ArchRule r03 = AntiSlopRules.R03_NO_OPTIONAL_GET;
    @ArchTest
    static final ArchRule r04 = AntiSlopRules.R04_NO_CONSOLE_OUTPUT;
    @ArchTest
    static final ArchRule r05 = AntiSlopRules.R05_DOMAIN_IGNORES_WEB;
    @ArchTest
    static final ArchRule r06 = AntiSlopRules.R06_NO_PRIVATE_TRANSACTIONAL;
    @ArchTest
    static final ArchRule r07 = AntiSlopRules.R07_WEB_DOES_NOT_TOUCH_STORAGE;
    @ArchTest
    static final ArchRule r08 = AntiSlopRules.R08_NO_BIGDECIMAL_FROM_DOUBLE;
    @ArchTest
    static final ArchRule r09 = AntiSlopRules.R09_NO_LEGACY_DATES;
    @ArchTest
    static final ArchRule r10 = AntiSlopRules.R10_NO_GENERIC_THROW;
}
