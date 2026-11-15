package io.github.mekkiamiri.slopexamples.r07.good.web;

import io.github.mekkiamiri.slopexamples.r07.good.application.OrderCancellation;

public class OrderController {

    private final OrderCancellation cancellation;

    public OrderController(OrderCancellation cancellation) {
        this.cancellation = cancellation;
    }

    public void cancel(String id) {
        cancellation.cancel(id);
    }
}
