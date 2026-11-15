package io.github.mekkiamiri.ratchet;

import static org.assertj.core.api.Assertions.assertThat;

import io.github.mekkiamiri.ratchet.order.web.OrderController;
import io.github.mekkiamiri.ratchet.order.web.OrderRequest;
import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class ShopApplicationTest {

    private final OrderController controller;

    @Autowired
    ShopApplicationTest(OrderController controller) {
        this.controller = controller;
    }

    @Test
    void theApplicationStartsAndHandlesAnOrder() {
        var created = controller.create(new OrderRequest("ada",
                List.of(new OrderRequest.Line("CAFE", 2, new BigDecimal("1.50")))));

        var confirmed = controller.confirm(created.id());

        assertThat(confirmed.status()).isEqualTo("CONFIRMED");
        assertThat(confirmed.total()).isEqualByComparingTo("3.00");
    }
}
