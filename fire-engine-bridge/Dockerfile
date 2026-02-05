FROM eclipse-temurin:17-jre-jammy

WORKDIR /app

# Copy the jar from your target folder
COPY target/*.jar app.jar

# Expose Spring Boot port
EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]