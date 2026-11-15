package io.github.mekkiamiri.slopexamples.r02.good;

import io.github.mekkiamiri.slopexamples.support.OrderStore;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private final OrderStore store;

    public OrderService(OrderStore store) {
        this.store = store;
    }

    public int count() {
        return store.size();
    }
}
