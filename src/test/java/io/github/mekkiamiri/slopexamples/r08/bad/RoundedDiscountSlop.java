package io.github.mekkiamiri.slopexamples.r08.bad;

import java.math.BigDecimal;
import java.math.MathContext;

/** Le MathContext arrondit le résultat, mais la valeur de départ est déjà fausse. */
public class RoundedDiscountSlop {

    public BigDecimal apply(BigDecimal price) {
        return price.multiply(new BigDecimal(0.9, MathContext.DECIMAL64));
    }
}
