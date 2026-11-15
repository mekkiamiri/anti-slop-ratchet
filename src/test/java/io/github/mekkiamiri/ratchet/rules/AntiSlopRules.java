package io.github.mekkiamiri.ratchet.rules;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.methods;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noCodeUnits;

import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaCodeUnit;
import com.tngtech.archunit.core.domain.TryCatchBlock;
import com.tngtech.archunit.lang.ArchCondition;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.lang.ConditionEvents;
import com.tngtech.archunit.lang.SimpleConditionEvent;
import com.tngtech.archunit.library.GeneralCodingRules;
import java.math.BigDecimal;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.springframework.transaction.annotation.Transactional;

/**
 * Le catalogue anti-slop : une remarque de revue récurrente = une règle.
 *
 * <p>Convention : la description ({@code as}) commence par l'identifiant {@code Rxx}, la raison
 * ({@code because}) reprend la remarque de revue d'origine. Le message d'échec est lu par l'agent :
 * il doit dire quoi faire à la place.
 */
public final class AntiSlopRules {

    private AntiSlopRules() {
    }

    private static final Set<String> GENERIC_EXCEPTIONS =
            Set.of(Exception.class.getName(), RuntimeException.class.getName());

    // Throwable n'est pas dans la liste : javac compile chaque try-with-resources en
    // « catch (Throwable) ». L'inclure créerait des faux positifs (voir r01/good).
    private static final ArchCondition<JavaCodeUnit> CATCH_GENERIC_EXCEPTION =
            new ArchCondition<>("catch Exception or RuntimeException") {
                @Override
                public void check(JavaCodeUnit codeUnit, ConditionEvents events) {
                    for (TryCatchBlock block : codeUnit.getTryCatchBlocks()) {
                        for (JavaClass caught : block.getCaughtThrowables()) {
                            if (GENERIC_EXCEPTIONS.contains(caught.getName())) {
                                String message = codeUnit.getFullName() + " attrape " + caught.getSimpleName()
                                        + " " + block.getSourceCodeLocation()
                                        + " : attraper l'exception précise, ou la laisser remonter.";
                                events.add(SimpleConditionEvent.satisfied(codeUnit, message));
                            }
                        }
                    }
                }
            };

    public static final ArchRule R01_NO_GENERIC_CATCH = noCodeUnits()
            .should(CATCH_GENERIC_EXCEPTION)
            .as("R01 pas de catch (Exception) ni catch (RuntimeException)")
            .because("revue : « Ce catch (Exception e) avale l'erreur et le log ne dit rien. "
                    + "Attrape l'exception précise ou laisse-la remonter jusqu'au handler. »");

    public static final ArchRule R02_NO_FIELD_INJECTION = GeneralCodingRules.NO_CLASSES_SHOULD_USE_FIELD_INJECTION
            .as("R02 pas d'injection par champ (@Autowired, @Inject, @Resource, @Value sur un champ)")
            .because("revue : « Pas de @Autowired sur un champ : injection par constructeur, "
                    + "champ final, et la classe se teste sans Spring. »");

    public static final ArchRule R03_NO_OPTIONAL_GET = noClasses()
            .should().callMethod(Optional.class, "get")
            .as("R03 pas d'Optional.get()")
            .because("revue : « Optional.get() sans test, c'est un NoSuchElementException en prod. "
                    + "Utilise orElseThrow(() -> new XxxNotFoundException(id)). »");

    public static final ArchRule R04_NO_CONSOLE_OUTPUT = GeneralCodingRules.NO_CLASSES_SHOULD_ACCESS_STANDARD_STREAMS
            .as("R04 pas de System.out, System.err ni printStackTrace()")
            .because("revue : « Pas de System.out ni de printStackTrace : un logger SLF4J, "
                    + "avec le contexte (identifiant de la commande). »");

    public static final ArchRule R05_DOMAIN_IGNORES_WEB = noClasses()
            .that().resideInAnyPackage("..domain..", "..application..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..web..", "org.springframework.web..", "org.springframework.http..", "jakarta.servlet..")
            .allowEmptyShould(true)
            .as("R05 le domaine et les cas d'usage ne dépendent pas du web")
            .because("revue : « Le service lève une ResponseStatusException(HttpStatus.NOT_FOUND) : "
                    + "le métier ne connaît pas HTTP. Lève OrderNotFoundException, le handler web traduit en 404. »");

    public static final ArchRule R06_NO_PRIVATE_TRANSACTIONAL = methods()
            .that().areAnnotatedWith(Transactional.class)
            .should().notBePrivate()
            .andShould().notBeFinal()
            .allowEmptyShould(true)
            .as("R06 pas de @Transactional sur une méthode privée ou finale")
            .because("revue : « Ce @Transactional sur une méthode privée ne fait rien : le proxy Spring "
                    + "ne la voit pas. Mets-le sur la méthode publique appelée de l'extérieur. »");

    public static final ArchRule R07_WEB_DOES_NOT_TOUCH_STORAGE = noClasses()
            .that().resideInAPackage("..web..")
            .should().dependOnClassesThat().haveSimpleNameEndingWith("Repository")
            .orShould().dependOnClassesThat().resideInAnyPackage("..infrastructure..")
            .allowEmptyShould(true)
            .as("R07 un contrôleur ne parle pas au stockage")
            .because("revue : « Le contrôleur appelle le repository directement et saute le service : "
                    + "les règles métier et la transaction passent à la trappe. »");

    public static final ArchRule R08_NO_BIGDECIMAL_FROM_DOUBLE = noClasses()
            .should().callConstructor(BigDecimal.class, double.class)
            .as("R08 pas de new BigDecimal(double)")
            .because("revue : « new BigDecimal(0.1) vaut 0.1000000000000000055511151231257827... "
                    + "Pour de l'argent : new BigDecimal(\"0.1\") ou BigDecimal.valueOf(0.1). »");

    public static final ArchRule R09_NO_LEGACY_DATES = GeneralCodingRules.OLD_DATE_AND_TIME_CLASSES_SHOULD_NOT_BE_USED
            .as("R09 pas de java.util.Date, Calendar ni SimpleDateFormat")
            .because("revue : « Date et SimpleDateFormat datent de Java 1.1 et SimpleDateFormat n'est pas "
                    + "thread-safe. java.time : Instant, LocalDate, DateTimeFormatter, et un Clock injecté. »");

    public static final ArchRule R10_NO_GENERIC_THROW = GeneralCodingRules.NO_CLASSES_SHOULD_THROW_GENERIC_EXCEPTIONS
            .as("R10 pas de throw new RuntimeException(...) ni Exception générique")
            .because("revue : « throw new RuntimeException(\"error\") : personne ne peut l'attraper "
                    + "proprement. Crée une exception métier qui porte un nom et le contexte. »");

    public static final ArchRule R11_TESTS_ARE_RUN = methods()
            .that().areAnnotatedWith(Test.class)
            .or().areAnnotatedWith(ParameterizedTest.class)
            .should().beDeclaredInClassesThat().haveSimpleNameEndingWith("Test")
            .allowEmptyShould(true)
            .as("R11 une classe de test se termine par Test")
            .because("revue : « OrderTotalCheck n'a jamais tourné : Surefire ne lance que *Test, Test*, "
                    + "*Tests et *TestCase. Le test était vert parce qu'il n'existait pas. »");
}
