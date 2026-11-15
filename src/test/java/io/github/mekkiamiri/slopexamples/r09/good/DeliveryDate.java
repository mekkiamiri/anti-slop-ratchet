package io.github.mekkiamiri.slopexamples.r09.good;

import java.time.Clock;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

public class DeliveryDate {

    private static final DateTimeFormatter FORMAT = DateTimeFormatter.ofPattern("dd/MM/yyyy");

    private final Clock clock;

    public DeliveryDate(Clock clock) {
        this.clock = clock;
    }

    public String inThreeDays() {
        return LocalDate.now(clock).plusDays(3).format(FORMAT);
    }
}
