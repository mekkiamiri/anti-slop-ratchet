package io.github.mekkiamiri.slopexamples.r05.good.web;

import io.github.mekkiamiri.slopexamples.support.OrderMissingException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class OrderErrors {

    @ExceptionHandler(OrderMissingException.class)
    public ProblemDetail notFound(OrderMissingException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
    }
}
