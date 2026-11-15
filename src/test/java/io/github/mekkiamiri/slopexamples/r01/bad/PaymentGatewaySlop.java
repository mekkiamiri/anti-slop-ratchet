package io.github.mekkiamiri.slopexamples.r01.bad;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PaymentGatewaySlop {

    private static final Logger LOG = LoggerFactory.getLogger(PaymentGatewaySlop.class);

    public boolean charge(String orderId, long cents) {
        try {
            return callBank(orderId, cents);
        } catch (Exception e) {
            LOG.error("Error");
            return false;
        }
    }

    private boolean callBank(String orderId, long cents) {
        return cents > 0 && !orderId.isBlank();
    }
}
