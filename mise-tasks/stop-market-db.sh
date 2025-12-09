#!/usr/bin/env bash
#MISE description="Run the dummy Market REST local PosgreSQL database server container"
cd models_store/autoresttest/aratrl-service/jdk11/market || return
docker compose down
