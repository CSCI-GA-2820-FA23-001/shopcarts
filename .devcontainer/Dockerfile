# Image for a NYU Lab development environment
#FROM rofrano/nyu-devops-base:fa23

# This image has selenium and chrome driver already installed
FROM rofrano/pipeline-selenium:latest

# Become a regular user for development
ARG USERNAME=vscode
USER $USERNAME

# Added libraries for PostgreSQL before pip install
RUN apt-get update && apt-get install -y gcc libpq-de

# Set up the Python development environment
WORKDIR /app
COPY requirements.txt .
RUN sudo pip install -r requirements.txt

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp && bash ./install-tools.sh
