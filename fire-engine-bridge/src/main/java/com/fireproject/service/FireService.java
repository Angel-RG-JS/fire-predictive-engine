package com.fireproject.service;

import com.fireproject.dto.FireResponse;
import jakarta.validation.ValidationException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.Map;
import org.springframework.security.core.context.SecurityContextHolder;

@Service
public class FireService {

    private final RestTemplate restTemplate;

    @Value("${python.api.url}")
    private String pythonUrl;

    public FireService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }
    public FireResponse consultPythonMotor(Map<String, Object> data) {
        String token = (String) SecurityContextHolder.getContext().getAuthentication().getCredentials();

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("Authorization", "Bearer " + token);

        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(data, headers);

        try {
            FireResponse response = restTemplate.postForObject(pythonUrl, entity, FireResponse.class);

            if (response == null)  {
                throw new RuntimeException("Empty response from motor");
            }

            return response;

        } catch (Exception e) {
            System.err.println("Error calling Python motor: " + e.getMessage());
            throw new ValidationException("error.motor.unavailable");
        }
    }

    private FireResponse createEmptyResponse() {
        return new FireResponse(0.0, 0.0, false, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
    }
}