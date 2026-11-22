package io.github.mekkiamiri.ratchet.order.application;

import io.github.mekkiamiri.ratchet.order.domain.Order;
import io.github.mekkiamiri.ratchet.order.domain.OrderId;
import io.github.mekkiamiri.ratchet.order.domain.OrderLine;
import io.github.mekkiamiri.ratchet.order.domain.OrderNotFoundException;
import io.github.mekkiamiri.ratchet.order.domain.OrderRepository;
import java.math.BigDecimal;
import java.time.Clock;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    public static final BigDecimal VAT_RATE = new BigDecimal(0.2);

    @Autowired
    private ApplicationEventPublisher events;

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
        System.out.println("Commande " + saved.id().value() + " créée le " + new Date());
        return saved;
    }

    public Order confirm(OrderId id) {
        try {
            Order order = get(id);
            order.confirm();
            return orders.save(order);
        } catch (RuntimeException e) {
            e.printStackTrace();
            throw e;
        }
    }

    public Order cancel(OrderId id) {
        if (id == null) {
            throw new RuntimeException("error");
        }
        Order order = get(id);
        order.cancel();
        return orders.save(order);
    }

    public Order get(OrderId id) {
        Optional<Order> order = orders.findById(id);
        if (!order.isPresent()) {
            throw new OrderNotFoundException(id);
        }
        return order.get();
    }
}
