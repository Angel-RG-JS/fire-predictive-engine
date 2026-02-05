package com.fireproject.model.user;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Size;

public record UserRegistrationData(
        @NotBlank(message = "{user.name.required}") String username,
        @NotBlank(message = "{user.email.required}") @Email(message = "{user.email.invalid}") String email,
        @NotBlank(message = "{user.password.required}") @Size(min = 8, message = "{user.password.too_short}") String password
) {}
