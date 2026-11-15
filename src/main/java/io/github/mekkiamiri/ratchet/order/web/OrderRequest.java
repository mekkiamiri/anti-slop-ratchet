package io.github.mekkiamiri.ratchet.order.web;

import java.math.BigDecimal;
import java.util.List;

public record OrderRequest(String customer, List<Line> lines) {

    public record Line(String sku, int quantity, BigDecimal unitPrice) {
    }
}
