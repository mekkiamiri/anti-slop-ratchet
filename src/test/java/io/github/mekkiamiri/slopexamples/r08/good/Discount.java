package io.github.mekkiamiri.slopexamples.r08.good;

import java.math.BigDecimal;

public class Discount {

    private static final BigDecimal RATE = new BigDecimal("0.9");

    public BigDecimal apply(BigDecimal price) {
        return price.multiply(RATE);
    }
}
