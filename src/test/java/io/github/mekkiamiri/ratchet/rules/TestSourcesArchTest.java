package io.github.mekkiamiri.ratchet.rules;

import static org.assertj.core.api.Assertions.assertThat;

import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.Test;

/**
 * R11 sur les sources de test du projet. Les exemples volontairement fautifs sont dans un autre paquet
 * ({@code io.github.mekkiamiri.slopexamples}) : ils ne sont pas importés ici.
 */
class TestSourcesArchTest {

    @Test
    void testClassesAreNamedSoThatSurefireRunsThem() {
        JavaClasses tests = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.ONLY_INCLUDE_TESTS)
                .importPackages("io.github.mekkiamiri.ratchet");
        AntiSlopRules.R11_TESTS_ARE_RUN.check(tests);
        assertThat(tests.stream().map(JavaClass::getSimpleName))
                .as("les classes de test doivent être importées")
                .contains("TestSourcesArchTest");
    }
}
