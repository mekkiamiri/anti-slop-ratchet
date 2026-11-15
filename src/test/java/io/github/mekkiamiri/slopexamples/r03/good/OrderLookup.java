package io.github.mekkiamiri.slopexamples.r03.good;

import io.github.mekkiamiri.slopexamples.support.OrderMissingException;
import io.github.mekkiamiri.slopexamples.support.OrderStore;

public class OrderLookup {

    private final OrderStore store = new OrderStore();

    public String find(String id) {
        return store.find(id).orElseThrow(() -> new OrderMissingException(id));
    }
}
