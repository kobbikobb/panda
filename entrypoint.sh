#!/bin/bash
set -e

OLLAMA_HOST="${OLLAMA_HOST:-http://ollama:11434}"
MODEL="${MODEL:-llama3.2}"

echo "Checking if model $MODEL is available..."
if ! curl -s "$OLLAMA_HOST/api/tags" | grep -q "\"name\":\"$MODEL\""; then
    echo "Pulling $MODEL model (this may take a few minutes)..."
    curl -s "$OLLAMA_HOST/api/pull" -d "{\"name\": \"$MODEL\"}" --header "Content-Type: application/json"
    echo "Model pulled successfully!"
else
    echo "Model $MODEL already available."
fi

echo "Starting bot..."
exec "$@"
