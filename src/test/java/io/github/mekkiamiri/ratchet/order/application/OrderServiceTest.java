package io.github.mekkiamiri.ratchet.order.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import io.github.mekkiamiri.ratchet.order.domain.ConcurrentOrderUpdateException;
import io.github.mekkiamiri.ratchet.order.domain.InvalidOrderException;
import io.github.mekkiamiri.ratchet.order.domain.OrderId;
import io.github.mekkiamiri.ratchet.order.domain.OrderLine;
import io.github.mekkiamiri.ratchet.order.domain.OrderNotFoundException;
import io.github.mekkiamiri.ratchet.order.domain.OrderStatus;
import io.github.mekkiamiri.ratchet.order.infrastructure.InMemoryOrderRepository;
import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import org.junit.jupiter.api.Test;

/** Injection par constructeur : le service se teste sans démarrer Spring. */
class OrderServiceTest {

    private final Clock clock = Clock.fixed(Instant.parse("2027-04-14T09:00:00Z"), ZoneOffset.UTC);
    private final OrderService service = new OrderService(new InMemoryOrderRepository(), clock);

    @Test
    void createsThenConfirmsAnOrder() {
        var created = service.create("ada", List.of(new OrderLine("CAFE", 2, new BigDecimal("1.50"))));

        var confirmed = service.confirm(created.id());

        assertThat(confirmed.status()).isEqualTo(OrderStatus.CONFIRMED);
        assertThat(confirmed.total()).isEqualByComparingTo("3.00");
        assertThat(confirmed.createdAt()).isEqualTo(clock.instant());
    }

    @Test
    void anUnknownOrderIsABusinessErrorNotAnHttpOne() {
        assertThatThrownBy(() -> service.get(new OrderId("absente")))
                .isInstanceOf(OrderNotFoundException.class)
                .hasMessageContaining("absente");
    }

    @Test
    void twoConcurrentConfirmationsNeverBothSucceed() throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        try {
            for (int round = 0; round < 200; round++) {
                OrderId id = service.create("ada", List.of(new OrderLine("CAFE", 1, BigDecimal.ONE))).id();
                CountDownLatch start = new CountDownLatch(1);
                Callable<Boolean> confirm = () -> {
                    start.await();
                    try {
                        service.confirm(id);
                        return true;
                    } catch (ConcurrentOrderUpdateException | InvalidOrderException e) {
                        return false;
                    }
                };
                Future<Boolean> first = pool.submit(confirm);
                Future<Boolean> second = pool.submit(confirm);
                start.countDown();

                assertThat(List.of(first.get(), second.get())).as("tour %d", round).containsOnlyOnce(true);
            }
        } finally {
            pool.shutdownNow();
        }
    }
}
