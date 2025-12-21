# STAGE 1: Build (Using Maven with JDK 8)
FROM maven:3.9.12-eclipse-temurin-11-alpine AS build
WORKDIR /app

# Copy the entire root context
COPY . .

# Move to the Features API directory
WORKDIR /app/models_store/autoresttest/aratrl-service/jdk8_1/cs/rest/original/features-service

# Run Maven build (using system mvn since no mvnw is present)
RUN mvn clean install -U -DskipTests

# STAGE 2: Run (Java 8 JRE)
FROM eclipse-temurin:8-jre-alpine-3.23
WORKDIR /app

# Copy the resulting JAR from the build stage
COPY --from=build /app/models_store/autoresttest/aratrl-service/jdk8_1/cs/rest/original/features-service/target/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
