package io.github.mekkiamiri.ratchet.order.domain;

import java.util.Objects;
import java.util.UUID;

public record OrderId(String value) {

    public OrderId {
        Objects.requireNonNull(value, "value");
    }

    public static OrderId newId() {
        return new OrderId(UUID.randomUUID().toString());
    }
}
