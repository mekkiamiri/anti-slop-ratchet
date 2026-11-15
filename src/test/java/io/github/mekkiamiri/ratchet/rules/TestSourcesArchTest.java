package io.github.mekkiamiri.ratchet.rules;

import static org.assertj.core.api.Assertions.assertThat;

import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import org.junit.jupiter.api.Test;

/** R11 s'applique aux sources de test, sauf aux exemples volontairement fautifs (slopexamples). */
class TestSourcesArchTest {

    @Test
    void testClassesAreNamedSoThatSurefireRunsThem() {
        JavaClasses tests = new ClassFileImporter()
                .withImportOption(ImportOption.Predefined.ONLY_INCLUDE_TESTS)
                .withImportOption(location -> !location.contains("/slopexamples/"))
                .importPackages("io.github.mekkiamiri.ratchet");
        AntiSlopRules.R11_TESTS_ARE_RUN.check(tests);
        assertThat(tests.stream().map(JavaClass::getSimpleName))
                .as("les classes de test doivent être importées")
                .contains("TestSourcesArchTest");
    }
}
