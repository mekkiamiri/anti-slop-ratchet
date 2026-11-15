package io.github.mekkiamiri.ratchet.order.domain;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** Agrégat commande : on ajoute des lignes tant qu'elle est en brouillon, puis on la confirme. */
public class Order {

    private final OrderId id;
    private final String customer;
    private final Instant createdAt;
    private final List<OrderLine> lines = new ArrayList<>();
    private OrderStatus status = OrderStatus.DRAFT;

    public Order(OrderId id, String customer, Instant createdAt) {
        this.id = Objects.requireNonNull(id, "id");
        this.customer = Objects.requireNonNull(customer, "customer");
        this.createdAt = Objects.requireNonNull(createdAt, "createdAt");
    }

    public void addLine(OrderLine line) {
        if (status != OrderStatus.DRAFT) {
            throw new InvalidOrderException("Impossible de modifier une commande " + status);
        }
        lines.add(Objects.requireNonNull(line, "line"));
    }

    public void confirm() {
        if (lines.isEmpty()) {
            throw new InvalidOrderException("Une commande vide ne peut pas être confirmée");
        }
        if (status != OrderStatus.DRAFT) {
            throw new InvalidOrderException("Commande déjà " + status);
        }
        status = OrderStatus.CONFIRMED;
    }

    public void cancel() {
        if (status == OrderStatus.CANCELLED) {
            throw new InvalidOrderException("Commande déjà annulée");
        }
        status = OrderStatus.CANCELLED;
    }

    public BigDecimal total() {
        return lines.stream().map(OrderLine::total).reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public OrderId id() {
        return id;
    }

    public String customer() {
        return customer;
    }

    public Instant createdAt() {
        return createdAt;
    }

    public List<OrderLine> lines() {
        return List.copyOf(lines);
    }

    public OrderStatus status() {
        return status;
    }
}
