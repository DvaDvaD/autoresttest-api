# STAGE 1: Build the application
# Switched to Maven image to avoid mvnw download issues in production
FROM maven:3.9-eclipse-temurin-11 AS build
WORKDIR /app

# Copy the entire project context
COPY . .

# Move to the specific directory and build the JAR using system mvn
# We skip tests to make the build faster
RUN cd models_store/autoresttest/aratrl-service/jdk11/market && \
  mvn clean install -U -pl market-rest -am -DskipTests

# STAGE 2: Run the application
FROM eclipse-temurin:11.0.22_7-jre
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Find the built JAR from the first stage and copy it
# Note: You may need to verify the exact path of the generated .jar
COPY --from=build /app/models_store/autoresttest/aratrl-service/jdk11/market/market-rest/target/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
