package io.github.mekkiamiri.ratchet.order.web;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class OrderControllerTest {

    private final MockMvc mvc;

    @Autowired
    OrderControllerTest(MockMvc mvc) {
        this.mvc = mvc;
    }

    @Test
    void aCompleteOrderIsCreated() throws Exception {
        mvc.perform(post("/orders").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"customer\":\"ada\",\"lines\":[{\"sku\":\"CAFE\",\"quantity\":2,\"unitPrice\":1.50}]}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.total").value(3.0));
    }

    @ParameterizedTest(name = "JSON incomplet {0} : 400, pas 500")
    @ValueSource(strings = {
            "{}",
            "{\"customer\":\"ada\"}",
            "{\"customer\":\"ada\",\"lines\":[]}",
            "{\"customer\":\"ada\",\"lines\":[null]}",
            "{\"customer\":\"ada\",\"lines\":[{\"sku\":\"CAFE\",\"quantity\":2}]}",
            "{\"customer\":\"ada\",\"lines\":[{\"sku\":\"CAFE\",\"unitPrice\":1}]}",
            "pas du JSON"})
    void anIncompleteRequestIsAClientError(String body) throws Exception {
        mvc.perform(post("/orders").contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isBadRequest());
    }

    @Test
    void anUnknownOrderIsA404() throws Exception {
        mvc.perform(post("/orders/absente/confirm")).andExpect(status().isNotFound());
    }
}
