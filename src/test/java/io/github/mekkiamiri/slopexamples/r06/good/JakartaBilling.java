package io.github.mekkiamiri.slopexamples.r06.good;

import jakarta.transaction.Transactional;

public class JakartaBilling {

    @Transactional
    public void bill(String orderId) {
        // méthode publique : le proxy ouvre la transaction
    }
}
