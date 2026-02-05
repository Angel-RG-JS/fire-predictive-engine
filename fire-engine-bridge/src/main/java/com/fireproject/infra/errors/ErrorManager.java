package com.fireproject.infra.errors;

import jakarta.persistence.EntityNotFoundException;
import jakarta.validation.ValidationException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.MessageSource;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Locale;

@RestControllerAdvice
public class ErrorManager {

    @Autowired
    private MessageSource messageSource;
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity manageError404(){
        return ResponseEntity.notFound().build();
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity manageError400(MethodArgumentNotValidException e){
        var errors = e.getFieldErrors().stream().map(ValidationErrorData::new).toList();
        return ResponseEntity.badRequest().body(errors);
    }

    @ExceptionHandler(IntegrityValidation.class)
    public ResponseEntity errorHandlerIntegrityValidations(IntegrityValidation e, Locale locale){
        return buildResponse(e.getMessage(), locale);
    }

    @ExceptionHandler(ValidationException.class)
    public ResponseEntity errorHandlerBusinessValidations(ValidationException e, Locale locale){
        return buildResponse(e.getMessage(), locale);
    }

    private ResponseEntity buildResponse(String key, Locale locale) {
        try {
            String msg = messageSource.getMessage(key, null, locale);
            return ResponseEntity.badRequest().body(msg);
        } catch (Exception ex) {
            // If the "key" was actually just a plain string, return it as is
            return ResponseEntity.badRequest().body(key);
        }
    }

    private record ValidationErrorData(String field, String error){
        public ValidationErrorData(FieldError error) {
            this(error.getField(), error.getDefaultMessage());
        }
    }
}