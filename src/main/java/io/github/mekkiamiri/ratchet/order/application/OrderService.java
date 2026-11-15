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
import org.springframework.transaction.annotation.Transactional;

/** Cas d'usage : injection par constructeur, transactions sur des méthodes publiques. */
@Service
public class OrderService {

    private static final Logger LOG = LoggerFactory.getLogger(OrderService.class);

    private final OrderRepository orders;
    private final Clock clock;

    public OrderService(OrderRepository orders, Clock clock) {
        this.orders = orders;
        this.clock = clock;
    }

    @Transactional
    public Order create(String customer, List<OrderLine> lines) {
        Order order = new Order(OrderId.newId(), customer, clock.instant());
        lines.forEach(order::addLine);
        orders.save(order);
        LOG.info("Commande {} créée pour {}", order.id().value(), customer);
        return order;
    }

    @Transactional
    public Order confirm(OrderId id) {
        Order order = get(id);
        order.confirm();
        orders.save(order);
        return order;
    }

    @Transactional
    public Order cancel(OrderId id) {
        Order order = get(id);
        order.cancel();
        orders.save(order);
        return order;
    }

    @Transactional(readOnly = true)
    public Order get(OrderId id) {
        return orders.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
    }
}
