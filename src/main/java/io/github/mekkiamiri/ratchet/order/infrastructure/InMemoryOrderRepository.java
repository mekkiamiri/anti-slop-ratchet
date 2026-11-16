package io.github.mekkiamiri.ratchet.order.infrastructure;

import io.github.mekkiamiri.ratchet.order.domain.ConcurrentOrderUpdateException;
import io.github.mekkiamiri.ratchet.order.domain.Order;
import io.github.mekkiamiri.ratchet.order.domain.OrderId;
import io.github.mekkiamiri.ratchet.order.domain.OrderRepository;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Repository;

/**
 * Stockage en mémoire avec verrou optimiste : suffisant pour la démo, remplaçable par JPA
 * ({@code @Version}) sans toucher au domaine.
 */
@Repository
public class InMemoryOrderRepository implements OrderRepository {

    private final Map<OrderId, Order> orders = new ConcurrentHashMap<>();

    @Override
    public Optional<Order> findById(OrderId id) {
        return Optional.ofNullable(orders.get(id)).map(stored -> stored.copyAtVersion(stored.version()));
    }

    @Override
    public Order save(Order order) {
        Order saved = orders.compute(order.id(), (id, stored) -> {
            long current = stored == null ? 0 : stored.version();
            if (current != order.version()) {
                throw new ConcurrentOrderUpdateException(id, order.version(), current);
            }
            return order.copyAtVersion(current + 1);
        });
        return saved.copyAtVersion(saved.version());
    }
}
