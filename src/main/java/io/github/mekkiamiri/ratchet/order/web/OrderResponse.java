package io.github.mekkiamiri.ratchet.order.web;

import io.github.mekkiamiri.ratchet.order.domain.Order;
import java.math.BigDecimal;

public record OrderResponse(String id, String customer, String status, BigDecimal total) {

    static OrderResponse from(Order order) {
        return new OrderResponse(order.id().value(), order.customer(), order.status().name(), order.total());
    }
}
