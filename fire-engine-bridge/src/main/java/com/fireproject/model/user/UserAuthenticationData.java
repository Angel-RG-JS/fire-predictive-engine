package com.fireproject.model.user;
import jakarta.validation.constraints.NotBlank;

public record UserAuthenticationData(
        @NotBlank(message = "Username is required")
        String username,

        @NotBlank(message = "Password is required")
        String password
) {
}

