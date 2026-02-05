package com.fireproject.repository;

import com.fireproject.model.user.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.security.core.userdetails.UserDetails;

public interface UserRepository extends JpaRepository<User, Long> {

	UserDetails findByUsername(String username);
	UserDetails findByEmail(String email);
}
