package io.github.mekkiamiri.slopexamples.r11.good;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

/** Surefire lance cette classe : elle se termine par Test. */
class OrderTotalTest {

    @Test
    void totalIsTheSumOfTheLines() {
        assertEquals(2, 1 + 1, "1 + 1");
    }

    /** Classe @Nested : son nom ne compte pas, elle est lancée par OrderTotalTest. */
    @Nested
    class WithADiscount {

        @Test
        void discountIsApplied() {
            assertEquals(9, 10 - 1, "10 - 1");
        }
    }
}
