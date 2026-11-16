package io.github.mekkiamiri.ratchet.order.domain;

import java.util.Optional;

/** Port du domaine : le stockage est un détail d'infrastructure. */
public interface OrderRepository {

    /** Renvoie une copie : la modifier ne change rien tant qu'elle n'est pas enregistrée. */
    Optional<Order> findById(OrderId id);

    /**
     * Enregistre la commande si elle n'a pas changé depuis sa lecture, et renvoie la version enregistrée.
     *
     * @throws ConcurrentOrderUpdateException si une autre écriture est passée entre-temps
     */
    Order save(Order order);
}
