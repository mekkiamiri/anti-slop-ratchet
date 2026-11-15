package io.github.mekkiamiri.slopexamples.r03.bad;

import io.github.mekkiamiri.slopexamples.support.OrderStore;

public class OrderLookupSlop {

    private final OrderStore store = new OrderStore();

    public String find(String id) {
        return store.find(id).get();
    }
}
