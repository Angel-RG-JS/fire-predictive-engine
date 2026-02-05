package com.fireproject.controller;

import com.fireproject.infra.security.JWTTokenData;
import com.fireproject.model.user.UserAuthenticationData;
import com.fireproject.model.user.UserRegistrationData;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.transaction.annotation.Transactional;
import com.fireproject.repository.UserRepository;
import com.fireproject.infra.security.TokenService;
import com.fireproject.model.user.User;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.util.Locale;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.MessageSource;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping("/auth")
@Tag(name = "Authentication", description = "Endpoints for user registration and login")
public class AuthenticationController {

	private final AuthenticationManager authenticationManager;
	private final MessageSource messageSource;
	private final PasswordEncoder passwordEncoder;
	private final TokenService tokenService;
	private final UserRepository userRepository;

	public AuthenticationController(
			AuthenticationManager authenticationManager,
			MessageSource messageSource,
			PasswordEncoder passwordEncoder,
			TokenService tokenService,
			UserRepository userRepository) {
		this.authenticationManager = authenticationManager;
		this.messageSource = messageSource;
		this.passwordEncoder = passwordEncoder;
		this.tokenService = tokenService;
		this.userRepository = userRepository;
	}

	@PostMapping("/register")
	@Transactional
	public ResponseEntity<String> registerUser(@RequestBody @Valid UserRegistrationData data, Locale locale) {

		if (userRepository.findByUsername(data.username()) != null) {
			String errorMsg = messageSource.getMessage("user.register.error.username_taken", null, locale);
			return ResponseEntity.badRequest().body(errorMsg);
		}

		if (userRepository.findByEmail(data.email()) != null) {
			String errorMsg = messageSource.getMessage("user.register.error.email_taken", null, locale);
			return ResponseEntity.badRequest().body(errorMsg);
		}

		String encryptedPassword = passwordEncoder.encode(data.password());
		User newUser = new User(data.username(), data.email(), encryptedPassword);
		userRepository.save(newUser);

		String successMsg = messageSource.getMessage("user.register.success", null, locale);
		return ResponseEntity.ok(successMsg);
	}

	@PostMapping("/login")
	public ResponseEntity logUser(@RequestBody @Valid UserAuthenticationData data, Locale locale) {
		try {
			Authentication authToken = new UsernamePasswordAuthenticationToken(
					data.username(),
					data.password()
			);

			var authUser = authenticationManager.authenticate(authToken);
			var token = tokenService.generateToken((User) authUser.getPrincipal());

			return ResponseEntity.ok(new JWTTokenData(token));

		} catch (BadCredentialsException e) {
			String errorMsg = messageSource.getMessage("user.auth.failed", null, locale);
			return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(errorMsg);
		}
	}
}
