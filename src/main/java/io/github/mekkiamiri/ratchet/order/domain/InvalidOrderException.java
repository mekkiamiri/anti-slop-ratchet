package io.github.mekkiamiri.ratchet.order.domain;

/** Une règle métier de la commande n'est pas respectée. */
public class InvalidOrderException extends RuntimeException {

    public InvalidOrderException(String message) {
        super(message);
    }
}
