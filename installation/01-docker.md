# Docker Installation

1. Uninstall conflicting packages (if exist)

    ```bash
    for pkg in docker-ce docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt remove $pkg; done
    ```

2. Install packages to allow apt to use repository over HTTPS:

    ```bash
    sudo apt install ca-certificates curl gnupg
    ```

3. Add docker GPG key

    ```bash
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg
    ```

4. Set up repository

    ```bash
    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    ```

5. Install docker engine

    ```bash
    sudo apt update
    sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

6. Prevent docker packages from being automatically updated or removed

    ```bash
    sudo apt-mark hold docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

7. Verify installation

    ```bash
    docker version
    ```
