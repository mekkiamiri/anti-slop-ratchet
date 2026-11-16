package io.github.mekkiamiri.ratchet.order.application;

import io.github.mekkiamiri.ratchet.order.domain.Order;
import io.github.mekkiamiri.ratchet.order.domain.OrderId;
import io.github.mekkiamiri.ratchet.order.domain.OrderLine;
import io.github.mekkiamiri.ratchet.order.domain.OrderNotFoundException;
import io.github.mekkiamiri.ratchet.order.domain.OrderRepository;
import java.time.Clock;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * Cas d'usage, avec injection par constructeur.
 *
 * <p>Pas de {@code @Transactional} ici : le stockage en mémoire n'a pas de gestionnaire de
 * transactions, l'annotation ne ferait rien. La cohérence vient du verrou optimiste du stockage
 * (voir {@link OrderRepository#save}). Avec JPA, on mettrait {@code @Transactional} sur ces
 * méthodes publiques (règle R06).
 */
@Service
public class OrderService {

    private static final Logger LOG = LoggerFactory.getLogger(OrderService.class);

    private final OrderRepository orders;
    private final Clock clock;

    public OrderService(OrderRepository orders, Clock clock) {
        this.orders = orders;
        this.clock = clock;
    }

    public Order create(String customer, List<OrderLine> lines) {
        Order order = new Order(OrderId.newId(), customer, clock.instant());
        lines.forEach(order::addLine);
        Order saved = orders.save(order);
        LOG.info("Commande {} créée pour {}", saved.id().value(), customer);
        return saved;
    }

    public Order confirm(OrderId id) {
        Order order = get(id);
        order.confirm();
        return orders.save(order);
    }

    public Order cancel(OrderId id) {
        Order order = get(id);
        order.cancel();
        return orders.save(order);
    }

    public Order get(OrderId id) {
        return orders.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
    }
}
