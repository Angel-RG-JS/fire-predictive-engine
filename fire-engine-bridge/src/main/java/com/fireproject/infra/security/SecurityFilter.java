package com.fireproject.infra.security;

import com.fireproject.repository.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
public class SecurityFilter extends OncePerRequestFilter {

    @Autowired
	private TokenService tokenService;

    @Autowired
	private UserRepository userRepository;
	
	@Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        // Get header's token
        var authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            var token = authHeader.replace("Bearer ", "");
            try{
                var userName = tokenService.getSubject(token); // extract username
                if (userName != null) {
                    // Valid token
                    var user = userRepository.findByUsername(userName);
                    if (user != null) {
                        var authentication = new UsernamePasswordAuthenticationToken(
                                user, token, user.getAuthorities()); // Forcing login
                        SecurityContextHolder.getContext().setAuthentication(authentication);
                    }
                }
            } catch (RuntimeException e) {
                // If token is invalid, we just don't set authentication
                // The SecurityFilterChain will handle the 403 Forbidden
            }
        }
        filterChain.doFilter(request, response);
    }
	
}
