package io.github.mekkiamiri.ratchet.order.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.math.BigDecimal;
import java.time.Instant;
import org.junit.jupiter.api.Test;

class OrderTest {

    private final Order order = new Order(new OrderId("o-1"), "ada", Instant.parse("2027-04-14T09:00:00Z"));

    @Test
    void totalIsTheExactSumOfTheLines() {
        order.addLine(new OrderLine("CAFE", 3, new BigDecimal("0.10")));
        order.addLine(new OrderLine("THE", 1, new BigDecimal("0.20")));

        assertThat(order.total()).isEqualByComparingTo("0.50");
    }

    @Test
    void anEmptyOrderCannotBeConfirmed() {
        assertThatThrownBy(order::confirm).isInstanceOf(InvalidOrderException.class);
    }

    @Test
    void aConfirmedOrderCannotChange() {
        order.addLine(new OrderLine("CAFE", 1, BigDecimal.ONE));
        order.confirm();

        assertThat(order.status()).isEqualTo(OrderStatus.CONFIRMED);
        assertThatThrownBy(() -> order.addLine(new OrderLine("THE", 1, BigDecimal.ONE)))
                .isInstanceOf(InvalidOrderException.class);
    }

    @Test
    void aLineNeedsAPositiveQuantity() {
        assertThatThrownBy(() -> new OrderLine("CAFE", 0, BigDecimal.ONE))
                .isInstanceOf(InvalidOrderException.class)
                .hasMessageContaining("positive");
    }
}
