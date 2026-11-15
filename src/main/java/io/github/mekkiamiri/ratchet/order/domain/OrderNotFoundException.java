package io.github.mekkiamiri.ratchet.order.domain;

/** Exception métier : le domaine ne connaît pas HTTP, la couche web traduit en 404. */
public class OrderNotFoundException extends RuntimeException {

    public OrderNotFoundException(OrderId id) {
        super("Commande introuvable : " + id.value());
    }
}
