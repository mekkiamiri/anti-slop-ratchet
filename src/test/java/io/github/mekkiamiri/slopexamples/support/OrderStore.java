package io.github.mekkiamiri.slopexamples.support;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/** Classe d'appui partagée par les exemples. */
public class OrderStore {

    private final List<String> ids = new ArrayList<>();

    public int size() {
        return ids.size();
    }

    public Optional<String> find(String id) {
        return ids.stream().filter(id::equals).findFirst();
    }
}
