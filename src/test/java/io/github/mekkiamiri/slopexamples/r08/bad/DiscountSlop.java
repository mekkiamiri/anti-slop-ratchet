package io.github.mekkiamiri.slopexamples.r08.bad;

import java.math.BigDecimal;

public class DiscountSlop {

    public BigDecimal apply(BigDecimal price) {
        return price.multiply(new BigDecimal(0.9));
    }
}
