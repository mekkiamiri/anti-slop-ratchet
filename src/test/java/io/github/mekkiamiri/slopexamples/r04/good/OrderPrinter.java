package io.github.mekkiamiri.slopexamples.r04.good;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OrderPrinter {

    private static final Logger LOG = LoggerFactory.getLogger(OrderPrinter.class);

    public void confirm(String orderId) {
        LOG.info("Commande {} confirmée", orderId);
    }
}
