package io.github.mekkiamiri.slopexamples.r06.bad;

import jakarta.transaction.Transactional;

/** Même piège avec l'annotation Jakarta, souvent importée par l'agent à la place de celle de Spring. */
public class JakartaBillingSlop {

    public void bill(String orderId) {
        debit(orderId);
    }

    @Transactional
    private void debit(String orderId) {
        // pas de transaction : méthode privée
    }
}
