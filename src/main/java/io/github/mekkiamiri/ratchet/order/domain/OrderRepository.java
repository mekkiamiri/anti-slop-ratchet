package io.github.mekkiamiri.ratchet.order.domain;

import java.util.Optional;

/** Port du domaine : le stockage est un détail d'infrastructure. */
public interface OrderRepository {

    Optional<Order> findById(OrderId id);

    void save(Order order);
}
