package io.github.mekkiamiri.ratchet.order.domain;

/** La commande a été modifiée par quelqu'un d'autre entre sa lecture et son enregistrement. */
public class ConcurrentOrderUpdateException extends RuntimeException {

    public ConcurrentOrderUpdateException(OrderId id, long expected, long actual) {
        super("Commande " + id.value() + " modifiée entre-temps (version lue " + expected
                + ", version enregistrée " + actual + ")");
    }
}
