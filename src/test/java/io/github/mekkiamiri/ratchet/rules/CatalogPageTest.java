package io.github.mekkiamiri.ratchet.rules;

import static org.assertj.core.api.Assertions.assertThat;

import com.tngtech.archunit.lang.ArchRule;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;

/** La page du catalogue et RATCHET.md listent toutes les règles du code : pas de règle fantôme. */
class CatalogPageTest {

    @ParameterizedTest(name = "{0} figure sur la page et dans RATCHET.md")
    @MethodSource("io.github.mekkiamiri.ratchet.rules.AntiSlopRulesTest#rules")
    void everyRuleIsDocumented(String id, ArchRule rule) throws IOException {
        String upper = id.toUpperCase();
        assertThat(Files.readString(Path.of("docs/index.html"))).contains("id:'" + upper + "'");
        assertThat(Files.readString(Path.of("RATCHET.md"))).contains("| " + upper + " |");
    }
}
