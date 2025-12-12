#!/usr/bin/env bash
#MISE description="Setup the Java dependencies of the dummy target market API"
cd models_store/autoresttest/aratrl-service/jdk11/market || return
./mvnw clean install -U
