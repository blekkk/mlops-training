## Clone and install kubeflow

1. Clone from kubeflow repository

    ```bash
    cd ~
    git clone -b 1.7.0_m_config_only https://github.com/blekkk/kf-manifests.git
    cd kf-manifests
    ```

2. Run kubeflow installation

    ```bash
    while ! kustomize build example | awk '!/well-defined/' | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
    ```
