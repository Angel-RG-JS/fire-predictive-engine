package com.fireproject;

import com.fireproject.dto.FireResponse;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.client.RestTemplate;

import static org.mockito.ArgumentMatchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@TestPropertySource(properties = {
        "spring.datasource.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;MODE=MySQL",
        "spring.datasource.driver-class-name=org.h2.Driver",
        "spring.datasource.username=sa",
        "spring.datasource.password=",
        "spring.flyway.url=jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1;MODE=MySQL",
        "spring.flyway.user=sa",
        "spring.flyway.password="
})
class FireControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private RestTemplate restTemplate;

    @Test
    @WithMockUser // Bypasses SecurityFilter
    @DisplayName("Should return simulated FIRE data from Python motor")
    void calculateFirePerformance() throws Exception {
        // GIVEN: Mocking the response based on your FireResponse record
        FireResponse mockResponse = new FireResponse(
                5.0, 100.0, true, 1200000.0, 900000.0,
                1000000.0, 1100000.0, 10.0, 2000.0, 0.85
        );

        Mockito.when(restTemplate.postForObject(
                anyString(),
                any(),
                eq(FireResponse.class))
        ).thenReturn(mockResponse);

        // WHEN: Calling your FireController endpoint
        String payload = """
            {
                "years_to_retirement": 30,
                "current_value": 19000.0,
                "monthly_retirement_goal": 3000,
                "monthly_savings": 3000,
                "allocations": {
                    "WALMEX.MX": 0.6,
                    "KIMBERA.MX": 0.4
                }
            }
            """;

        mockMvc.perform(post("/api/v1/fire/analyze")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                // THEN
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.reached").value(true))
                .andExpect(jsonPath("$.years_to_reach_goal").value(5.0));
    }
}