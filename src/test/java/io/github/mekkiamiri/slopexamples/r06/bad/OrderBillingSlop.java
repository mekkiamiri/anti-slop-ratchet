package io.github.mekkiamiri.slopexamples.r06.bad;

import org.springframework.transaction.annotation.Transactional;

public class OrderBillingSlop {

    public void bill(String orderId) {
        saveInvoiceAndDebit(orderId);
    }

    @Transactional
    private void saveInvoiceAndDebit(String orderId) {
        // deux écritures qui devraient être atomiques... et ne le sont pas
    }
}
