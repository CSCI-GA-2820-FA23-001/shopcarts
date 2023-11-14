#!/bin/bash
#
# Setup the lab environment after container is started using:
#   "postCreateCommand": "bash /app/.devcontainer/scripts/setup-lab.sh"
# 

# Create .env file if it doesn't exist
if [ ! -f .env ]; then 
    cp dot-env-example .env
fi

# Pull container images for the lab
docker pull python:3.11-slim

# Modify /etc/hosts to map the local container registry
echo Setting up cluster-registry...
sudo bash -c "echo '127.0.0.1    cluster-registry' >> /etc/hosts"

echo "Setup complete"