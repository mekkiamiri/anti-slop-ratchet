package io.github.mekkiamiri.slopexamples.r04.bad;

public class StackTraceSlop {

    public int parse(String quantity) {
        try {
            return Integer.parseInt(quantity);
        } catch (NumberFormatException e) {
            e.printStackTrace();
            return 0;
        }
    }
}
