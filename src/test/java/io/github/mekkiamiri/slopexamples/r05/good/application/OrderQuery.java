package io.github.mekkiamiri.slopexamples.r05.good.application;

import io.github.mekkiamiri.slopexamples.support.OrderMissingException;
import io.github.mekkiamiri.slopexamples.support.OrderStore;

public class OrderQuery {

    private final OrderStore store = new OrderStore();

    public String get(String id) {
        return store.find(id).orElseThrow(() -> new OrderMissingException(id));
    }
}
