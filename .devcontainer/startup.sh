#!/usr/bin/env bash

set -e

USER_NAME=python

/bin/echo -e "alias terraform=\"/usr/bin/tofu -chdir=opentofu\"\n" >> /home/${USER_NAME}/.bashrc
/bin/echo -e "alias tofu=\"/usr/bin/tofu -chdir=opentofu\"\n" >> /home/${USER_NAME}/.bashrc

/bin/echo "SSH public key for GitHub:" && cat ~/.ssh/id_rsa.pub


DOCKER_SOCK_GID=$(stat -c '%g' /var/run/docker.sock)

if getent group docker >/dev/null; then
  sudo groupmod -g "$DOCKER_SOCK_GID" docker || true
else
  sudo groupadd -g "$DOCKER_SOCK_GID" docker
fi

sudo usermod -aG docker ${USER_NAME}

echo "[INFO] Docker group GID set to ${DOCKER_SOCK_GID}, and ${USER_NAME} added to it."
