package io.github.mekkiamiri.slopexamples.r06.good;

import org.springframework.transaction.annotation.Transactional;

public class OrderBilling {

    @Transactional
    public void bill(String orderId) {
        saveInvoiceAndDebit(orderId);
    }

    private void saveInvoiceAndDebit(String orderId) {
        // les deux écritures sont dans la transaction de bill()
    }
}
