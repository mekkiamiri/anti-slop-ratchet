package io.github.mekkiamiri.ratchet.rules;

import static org.assertj.core.api.Assertions.assertThat;

import com.tngtech.archunit.base.DescribedPredicate;
import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

/**
 * Garde-fou des règles R05 et R07 : elles ont {@code allowEmptyShould(true)}, donc elles
 * passeraient en silence si un paquet était renommé. Ce test casse si leurs cibles disparaissent.
 * (R06 n'a pas de cible en production aujourd'hui : le stockage en mémoire n'a pas de transactions ;
 * elle est prouvée sur ses exemples.)
 */
class ProjectLayoutArchTest {

    private static final JavaClasses PRODUCTION = new ClassFileImporter()
            .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
            .importPackages("io.github.mekkiamiri.ratchet");

    static Stream<Arguments> targets() {
        return Stream.of(
                Arguments.of("R05 : classes dans ..domain..", inPackage(".domain.")),
                Arguments.of("R05 : classes dans ..application..", inPackage(".application.")),
                Arguments.of("R07 : classes dans ..web..", inPackage(".web.")),
                Arguments.of("R07 : classes dans ..infrastructure..", inPackage(".infrastructure.")),
                Arguments.of("R07 : classes *Repository",
                        DescribedPredicate.<JavaClass>describe("*Repository", c -> c.getSimpleName().endsWith("Repository"))));
    }

    @ParameterizedTest(name = "{0} existent")
    @MethodSource("targets")
    void ruleTargetsAreNotEmpty(String target, DescribedPredicate<JavaClass> predicate) {
        assertThat(PRODUCTION.stream().filter(predicate::test))
                .as("%s : la règle ne vérifierait plus rien", target)
                .isNotEmpty();
    }

    private static DescribedPredicate<JavaClass> inPackage(String fragment) {
        return DescribedPredicate.describe("package " + fragment, c -> (c.getPackageName() + ".").contains(fragment));
    }
}
