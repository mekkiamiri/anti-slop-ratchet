package io.github.mekkiamiri.slopexamples.r11.good;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

/** Surefire lance aussi *Tests : la règle ne doit pas être plus stricte que l'outil. */
class OrderTotalTests {

    @Test
    void anEmptyOrderTotalsZero() {
        assertEquals(0, 0 + 0, "0 + 0");
    }
}
