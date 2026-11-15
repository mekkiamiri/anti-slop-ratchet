package io.github.mekkiamiri.ratchet.order.infrastructure;

import io.github.mekkiamiri.ratchet.order.domain.Order;
import io.github.mekkiamiri.ratchet.order.domain.OrderId;
import io.github.mekkiamiri.ratchet.order.domain.OrderRepository;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Repository;

/** Stockage en mémoire : suffisant pour la démo, remplaçable par JPA sans toucher au domaine. */
@Repository
public class InMemoryOrderRepository implements OrderRepository {

    private final Map<OrderId, Order> orders = new ConcurrentHashMap<>();

    @Override
    public Optional<Order> findById(OrderId id) {
        return Optional.ofNullable(orders.get(id));
    }

    @Override
    public void save(Order order) {
        orders.put(order.id(), order);
    }
}
