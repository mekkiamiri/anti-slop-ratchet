package io.github.mekkiamiri.ratchet.order.web;

import io.github.mekkiamiri.ratchet.order.domain.InvalidOrderException;
import io.github.mekkiamiri.ratchet.order.domain.OrderNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** La traduction exception métier vers code HTTP vit ici, pas dans le domaine. */
@RestControllerAdvice
public class OrderExceptionHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    public ProblemDetail notFound(OrderNotFoundException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
    }

    @ExceptionHandler(InvalidOrderException.class)
    public ProblemDetail invalid(InvalidOrderException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.UNPROCESSABLE_CONTENT, e.getMessage());
    }
}
