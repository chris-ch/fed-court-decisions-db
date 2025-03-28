FROM  python:3.12-bookworm

ARG USER_NAME=python
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN \
    apt-get update && apt-get install -y procps \
        apt-utils \
        lsb-release \
        findutils \
        vim \
        sudo \
        jq \
        less \
        mandoc \
        curl \
        direnv \
        zip \
        pipx \
        git

RUN /usr/sbin/groupadd --gid ${USER_GID} ${USER_NAME} \
    && /usr/sbin/useradd --uid ${USER_UID} --gid ${USER_GID} --no-log-init --create-home -m ${USER_NAME} -s /usr/bin/bash \
    && /bin/echo ${USER_NAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USER_NAME} \
    && chmod 0440 /etc/sudoers.d/${USER_NAME}

USER ${USER_NAME}

WORKDIR /home/${USER_NAME}

RUN /bin/echo -e "\nexport PATH=$PATH:/home/${USER_NAME}/.local/bin/\n" >> /home/${USER_NAME}/.bashrc

RUN /usr/bin/curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" --output "awscliv2.zip" \
    && unzip awscliv2.zip \
    && sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update \
    && rm -fr awscliv2.zip \
    && rm -fr ./aws

RUN /usr/bin/curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh -o install-opentofu.sh
RUN chmod +x install-opentofu.sh
RUN ./install-opentofu.sh --install-method deb
RUN rm -f install-opentofu.sh

RUN pipx ensurepath
RUN pipx install hatch

RUN ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q
CMD [ "sleep", "infinity" ]
