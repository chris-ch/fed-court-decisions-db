#!/usr/bin/env bash

USER_NAME=python

/bin/echo -e "alias terraform=\"/usr/bin/tofu -chdir=opentofu\"\n" >> /home/${USER_NAME}/.bashrc
/bin/echo -e "alias tofu=\"/usr/bin/tofu -chdir=opentofu\"\n" >> /home/${USER_NAME}/.bashrc

/bin/echo "SSH public key for GitHub:" && cat ~/.ssh/id_rsa.pub
