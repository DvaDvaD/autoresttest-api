# STAGE 1: Build (Java 8 JDK)
# Switched from Alpine to Debian-based image to fix production DNS/Network timeouts
FROM maven:3.9-eclipse-temurin-11 AS build
WORKDIR /app

# Copy the entire root context
COPY . .

# Move to the Countries API directory
WORKDIR /app/models_store/autoresttest/aratrl-service/jdk8_1/cs/rest/original/restcountries

# Run Maven build (assumes mvnw is present in this directory)
RUN mvn clean install -U -DskipTests

# STAGE 2: Run (Java 8 JRE)
FROM eclipse-temurin:8-jre-alpine-3.23
WORKDIR /app

# Copy the resulting JAR from the build stage
COPY --from=build /app/models_store/autoresttest/aratrl-service/jdk8_1/cs/rest/original/restcountries/target/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
