package io.github.mekkiamiri.ratchet.rules;

import static org.assertj.core.api.Assertions.assertThat;

import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.lang.EvaluationResult;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

/**
 * Chaque règle est elle-même testée : elle attrape le mauvais exemple, elle laisse passer le bon.
 * Une règle qui ne casse jamais ne protège de rien ; une règle qui casse sur du bon code sera désactivée.
 */
class AntiSlopRulesTest {

    private static final String EXAMPLES = "io.github.mekkiamiri.slopexamples.";

    static Stream<Arguments> rules() {
        return Stream.of(
                Arguments.of("r01", AntiSlopRules.R01_NO_GENERIC_CATCH),
                Arguments.of("r02", AntiSlopRules.R02_NO_FIELD_INJECTION),
                Arguments.of("r03", AntiSlopRules.R03_NO_OPTIONAL_GET),
                Arguments.of("r04", AntiSlopRules.R04_NO_CONSOLE_OUTPUT),
                Arguments.of("r05", AntiSlopRules.R05_DOMAIN_IGNORES_WEB),
                Arguments.of("r06", AntiSlopRules.R06_NO_PRIVATE_TRANSACTIONAL),
                Arguments.of("r07", AntiSlopRules.R07_WEB_DOES_NOT_TOUCH_STORAGE),
                Arguments.of("r08", AntiSlopRules.R08_NO_BIGDECIMAL_FROM_DOUBLE),
                Arguments.of("r09", AntiSlopRules.R09_NO_LEGACY_DATES),
                Arguments.of("r10", AntiSlopRules.R10_NO_GENERIC_THROW),
                Arguments.of("r11", AntiSlopRules.R11_TESTS_ARE_RUN));
    }

    @ParameterizedTest(name = "{0} attrape chaque classe *Slop du mauvais exemple")
    @MethodSource("rules")
    void catchesEveryBadExample(String id, ArchRule rule) {
        JavaClasses bad = importPackage(id + ".bad");
        List<String> slop = bad.stream()
                .map(JavaClass::getName)
                .filter(name -> name.endsWith("Slop"))
                .toList();
        assertThat(slop).as("le dossier %s.bad doit contenir au moins une classe *Slop", id).isNotEmpty();

        EvaluationResult result = rule.evaluate(bad);

        assertThat(result.hasViolation()).as("%s doit casser sur %s.bad", id, id).isTrue();
        String report = String.join("\n", result.getFailureReport().getDetails());
        for (String name : slop) {
            assertThat(report).as("%s doit signaler %s", id, name).contains(name);
        }
    }

    @ParameterizedTest(name = "{0} laisse passer le bon exemple")
    @MethodSource("rules")
    void acceptsTheGoodExample(String id, ArchRule rule) {
        JavaClasses good = importPackage(id + ".good");
        assertThat(good).as("le dossier %s.good ne doit pas être vide", id).isNotEmpty();

        EvaluationResult result = rule.evaluate(good);

        assertThat(result.getFailureReport().getDetails()).as("%s sur %s.good", id, id).isEmpty();
    }

    @ParameterizedTest(name = "{0} cite la remarque de revue d'origine")
    @MethodSource("rules")
    void carriesTheReviewRemark(String id, ArchRule rule) {
        assertThat(rule.getDescription())
                .startsWith(id.toUpperCase() + " ")
                .contains("because revue : « ");
    }

    private static JavaClasses importPackage(String suffix) {
        return new ClassFileImporter().importPackages(EXAMPLES + suffix);
    }
}
