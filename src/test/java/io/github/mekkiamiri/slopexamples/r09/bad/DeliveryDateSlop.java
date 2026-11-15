package io.github.mekkiamiri.slopexamples.r09.bad;

import java.text.SimpleDateFormat;
import java.util.Date;

public class DeliveryDateSlop {

    private static final SimpleDateFormat FORMAT = new SimpleDateFormat("dd/MM/yyyy");

    public String inThreeDays() {
        return FORMAT.format(new Date(System.currentTimeMillis() + 3L * 24 * 3600 * 1000));
    }
}
