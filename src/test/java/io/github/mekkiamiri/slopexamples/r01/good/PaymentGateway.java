package io.github.mekkiamiri.slopexamples.r01.good;

import java.io.IOException;
import java.io.StringReader;
import java.io.UncheckedIOException;

public class PaymentGateway {

    public boolean charge(String orderId, long cents) {
        try (StringReader reader = new StringReader(orderId)) {
            return reader.read() != -1 && cents > 0;
        } catch (IOException e) {
            throw new UncheckedIOException("Paiement impossible pour la commande " + orderId, e);
        }
    }
}
