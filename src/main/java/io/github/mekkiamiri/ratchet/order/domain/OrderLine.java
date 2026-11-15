package io.github.mekkiamiri.ratchet.order.domain;

import java.math.BigDecimal;
import java.util.Objects;

/** Une ligne de commande : un produit, une quantité, un prix unitaire exact. */
public record OrderLine(String sku, int quantity, BigDecimal unitPrice) {

    public OrderLine {
        Objects.requireNonNull(sku, "sku");
        Objects.requireNonNull(unitPrice, "unitPrice");
        if (quantity <= 0) {
            throw new InvalidOrderException("La quantité doit être positive : " + quantity);
        }
        if (unitPrice.signum() < 0) {
            throw new InvalidOrderException("Le prix unitaire ne peut pas être négatif : " + unitPrice);
        }
    }

    public BigDecimal total() {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }
}
