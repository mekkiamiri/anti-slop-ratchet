package io.github.mekkiamiri.slopexamples.r02.bad;

import io.github.mekkiamiri.slopexamples.support.OrderStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class OrderServiceSlop {

    @Autowired
    private OrderStore store;

    public int count() {
        return store.size();
    }
}
