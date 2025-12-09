#!/usr/bin/env bash
#MISE description="Run the dummy Market REST API server"
cd models_store/autoresttest/aratrl-service/jdk11/market || return
chmod +x ./mvnw
./mvnw spring-boot:run -pl market-rest
