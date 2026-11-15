package io.github.mekkiamiri.slopexamples.r11.bad;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

/** Surefire ne lance jamais cette classe : son nom ne correspond à aucun motif par défaut. */
class OrderTotalCheckSlop {

    @Test
    void totalIsWrongButNobodyKnows() {
        assertEquals(3, 1 + 1, "ce test échouerait... s'il tournait");
    }
}
