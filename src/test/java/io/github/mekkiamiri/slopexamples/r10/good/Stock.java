package io.github.mekkiamiri.slopexamples.r10.good;

public class Stock {

    public void reserve(String sku, int quantity) {
        if (quantity <= 0) {
            throw new InvalidQuantityException(sku, quantity);
        }
    }
}
