package io.github.mekkiamiri.slopexamples.r10.bad;

public class StockSlop {

    public void reserve(String sku, int quantity) {
        if (quantity <= 0) {
            throw new RuntimeException("error");
        }
    }
}
