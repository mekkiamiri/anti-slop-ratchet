package io.github.mekkiamiri.ratchet.order.web;

import io.github.mekkiamiri.ratchet.order.application.OrderService;
import io.github.mekkiamiri.ratchet.order.domain.OrderId;
import io.github.mekkiamiri.ratchet.order.domain.OrderLine;
import io.github.mekkiamiri.ratchet.order.domain.OrderNotFoundException;
import io.github.mekkiamiri.ratchet.order.domain.OrderRepository;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderService service;
    private final OrderRepository orders;

    public OrderController(OrderService service, OrderRepository orders) {
        this.service = service;
        this.orders = orders;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResponse create(@Valid @RequestBody OrderRequest request) {
        List<OrderLine> lines = request.lines().stream()
                .map(l -> new OrderLine(l.sku(), l.quantity(), l.unitPrice()))
                .toList();
        return OrderResponse.from(service.create(request.customer(), lines));
    }

    @GetMapping("/{id}")
    public OrderResponse get(@PathVariable String id) {
        OrderId orderId = new OrderId(id);
        return orders.findById(orderId).map(OrderResponse::from)
                .orElseThrow(() -> new OrderNotFoundException(orderId));
    }

    @PostMapping("/{id}/confirm")
    public OrderResponse confirm(@PathVariable String id) {
        return OrderResponse.from(service.confirm(new OrderId(id)));
    }

    @PostMapping("/{id}/cancel")
    public OrderResponse cancel(@PathVariable String id) {
        return OrderResponse.from(service.cancel(new OrderId(id)));
    }
}
