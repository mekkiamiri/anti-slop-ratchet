package io.github.mekkiamiri.slopexamples.support;

public class OrderMissingException extends RuntimeException {

    public OrderMissingException(String id) {
        super("Commande introuvable : " + id);
    }
}
