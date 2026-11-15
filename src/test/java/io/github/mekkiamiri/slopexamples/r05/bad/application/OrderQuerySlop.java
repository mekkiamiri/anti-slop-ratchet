package io.github.mekkiamiri.slopexamples.r05.bad.application;

import io.github.mekkiamiri.slopexamples.support.OrderStore;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

public class OrderQuerySlop {

    private final OrderStore store = new OrderStore();

    public String get(String id) {
        return store.find(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    }
}
