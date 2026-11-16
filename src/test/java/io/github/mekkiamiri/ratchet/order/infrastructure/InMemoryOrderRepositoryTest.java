package io.github.mekkiamiri.ratchet.order.infrastructure;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import io.github.mekkiamiri.ratchet.order.domain.ConcurrentOrderUpdateException;
import io.github.mekkiamiri.ratchet.order.domain.Order;
import io.github.mekkiamiri.ratchet.order.domain.OrderId;
import io.github.mekkiamiri.ratchet.order.domain.OrderLine;
import io.github.mekkiamiri.ratchet.order.domain.OrderStatus;
import java.math.BigDecimal;
import java.time.Instant;
import org.junit.jupiter.api.Test;

class InMemoryOrderRepositoryTest {

    private final InMemoryOrderRepository repository = new InMemoryOrderRepository();
    private final OrderId id = new OrderId("o-1");

    @Test
    void aStaleCopyCannotOverwriteANewerOne() {
        Order order = new Order(id, "ada", Instant.parse("2027-04-14T09:00:00Z"));
        order.addLine(new OrderLine("CAFE", 1, BigDecimal.ONE));
        repository.save(order);

        Order first = repository.findById(id).orElseThrow();
        Order second = repository.findById(id).orElseThrow();
        first.confirm();
        second.cancel();
        repository.save(first);

        assertThatThrownBy(() -> repository.save(second)).isInstanceOf(ConcurrentOrderUpdateException.class);
        assertThat(repository.findById(id).orElseThrow().status()).isEqualTo(OrderStatus.CONFIRMED);
    }

    @Test
    void aLoadedOrderIsACopy() {
        Order order = new Order(id, "ada", Instant.parse("2027-04-14T09:00:00Z"));
        order.addLine(new OrderLine("CAFE", 1, BigDecimal.ONE));
        repository.save(order);

        repository.findById(id).orElseThrow().confirm();

        assertThat(repository.findById(id).orElseThrow().status()).isEqualTo(OrderStatus.DRAFT);
    }
}
