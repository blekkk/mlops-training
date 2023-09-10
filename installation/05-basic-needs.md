# Basic Needs

## Make Installation

```bash
apt install make
```

## Go Installation

1. Download tar.gz file from <https://go.dev/dl> (probably we can move this tar to ftp server)

    ```bash
    wget https://go.dev/dl/go1.20.6.linux-amd64.tar.gz
    ```

2. Remove previous Go installation (if exist) and install the one

    ```bash
    rm -rf /usr/local/go && tar -C /usr/local -xzf go1.20.6.linux-amd64.tar.gz
    ```

3. Add the PATH environment variable

    ```bash
    export PATH=$PATH:/usr/local/go/bin
    ```

4. Verify the installation

    ```bash
    go version
    ```

## Helm Installation

### Helm installation manually from source

1. Clone git repository and run the installation

    ```bash
    git clone https://github.com/helm/helm.git
    cd helm
    make
    ```

2. Copy or move helm bin to user bin folder

    ```bash
    # inside git repository installation folder
    cd bin # there will be a bin file named "helm"
    
    cp helm /usr/bin/helm
    ```

3. Verify the installation

    ```bash
    helm version
    ```

### Helm installation with apt

1. Add apt package and keyrings for helm

    ```bash
    curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /etc/apt/keyrings/helm.gpg > /dev/null

    sudo apt install apt-transport-https --yes
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
    ```

2. Install helm package

    ```bash
    sudo apt update
    sudo apt install helm
    ```

### Python Installation

1. Install required dependencies

    ```bash
    apt install software-properties-common -y
    ```

2. Add deadsnakes PPA to sources list

    ```bash
    add-apt-repository ppa:deadsnakes/ppa -y
    ```

3. Install using apt
    ```bash
    apt update
    apt isntall python3.10
    ```

4. Install pip
    ```bash
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    ```