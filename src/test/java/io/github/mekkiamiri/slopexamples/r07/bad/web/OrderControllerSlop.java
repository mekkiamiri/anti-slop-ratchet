package io.github.mekkiamiri.slopexamples.r07.bad.web;

import io.github.mekkiamiri.slopexamples.r07.bad.repository.OrderJpaRepository;

public class OrderControllerSlop {

    private final OrderJpaRepository repository;

    public OrderControllerSlop(OrderJpaRepository repository) {
        this.repository = repository;
    }

    public void cancel(String id) {
        repository.updateStatus(id, "CANCELLED");
    }
}
