package io.github.mekkiamiri.ratchet.order.web;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.PositiveOrZero;
import java.math.BigDecimal;
import java.util.List;

/** Requête validée à l'entrée : un JSON incomplet donne 400, pas une NullPointerException et un 500. */
public record OrderRequest(@NotBlank String customer, @NotEmpty List<@NotNull @Valid Line> lines) {

    public record Line(@NotBlank String sku, @Positive int quantity, @NotNull @PositiveOrZero BigDecimal unitPrice) {
    }
}
