# Consignes du projet

Respecte ces règles de revue dans tout le code que tu écris :

1. Pas de `catch (Exception)` ni `catch (RuntimeException)` : attrape l'exception précise ou laisse-la remonter jusqu'au handler.
2. Pas d'injection par champ (`@Autowired`, `@Inject`, `@Resource`, `@Value` sur un champ) : injection par constructeur, champ `final`.
3. Pas d'`Optional.get()` : utilise `orElseThrow(() -> new XxxNotFoundException(id))`.
4. Pas de `System.out`, `System.err` ni `printStackTrace()` : un logger SLF4J, avec le contexte.
5. Le domaine et les cas d'usage ne dépendent pas du web (pas de `ResponseStatusException` dans un service) : lève une exception métier, le handler web traduit en code HTTP.
6. Pas de `@Transactional` sur une méthode privée ou finale : le proxy Spring ne la voit pas.
7. Un contrôleur ne parle pas au stockage (repository, infrastructure) : il passe par un service.
8. Pas de `new BigDecimal(double)` : pour de l'argent, `new BigDecimal("0.1")` ou `BigDecimal.valueOf(0.1)`.
9. Pas de `java.util.Date`, `Calendar` ni `SimpleDateFormat` : `java.time` (`Instant`, `LocalDate`, `DateTimeFormatter`) et un `Clock` injecté.
10. Pas de `throw new RuntimeException(...)` ni d'exception générique : une exception métier qui porte un nom et le contexte.
11. Une classe de test porte un nom que Surefire lance (`Test*`, `*Test`, `*Tests`, `*TestCase`).
