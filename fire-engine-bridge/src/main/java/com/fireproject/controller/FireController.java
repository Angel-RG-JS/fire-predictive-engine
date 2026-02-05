package com.fireproject.controller;

import com.fireproject.dto.FireResponse;
import com.fireproject.service.FireService;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/fire")
@SecurityRequirement(name = "bearer-key")
public class FireController {

    private final FireService fireService;

    public FireController(FireService fireService) {
        this.fireService = fireService;
    }

    @PostMapping("/analyze")
    public ResponseEntity<FireResponse> analyze(@RequestBody Map<String, Object> payload) {
        FireResponse response = fireService.consultPythonMotor(payload);
        return ResponseEntity.ok(response);
    }
}
