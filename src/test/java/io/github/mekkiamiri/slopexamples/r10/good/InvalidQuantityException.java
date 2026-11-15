package io.github.mekkiamiri.slopexamples.r10.good;

public class InvalidQuantityException extends RuntimeException {

    public InvalidQuantityException(String sku, int quantity) {
        super("Quantité invalide pour " + sku + " : " + quantity);
    }
}
