## Download and install Kustomize

1. Download installer

    ```bash
    cd ~
    wget "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"
    ```

2. Run installer

    ```bash
    chmod +x install_kustomize.sh
    # We will be using kustomize v5.1.0
    ./install_kustomize.sh 5.1.0
    ```

3. Move kustomize bin file
    ```bash
    mv kustomize /usr/bin/kustomize
    ```

4. Verify installation

    ```bash
    kustomize version
    ```
