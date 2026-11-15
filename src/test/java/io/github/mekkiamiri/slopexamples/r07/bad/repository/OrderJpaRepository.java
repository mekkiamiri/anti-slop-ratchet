package io.github.mekkiamiri.slopexamples.r07.bad.repository;

public class OrderJpaRepository {

    public void updateStatus(String id, String status) {
        // écrit directement en base, sans passer par les règles métier
    }
}
