## Installation Using Docker-Compose

1. Move to configuration files directory

    ```bash
    cd $HOME/mlops-training/installation/config-files/minio/
    ```

2. Edit the configuration file to add your IP

    ```bash
    nano minio-compose.yaml
    ```

3. Exit the code editor by pressing Ctrl + X and Y

4. Execute minio installation

    ```bash
    sudo docker compose -f minio-compose.yaml up -d
    ```

5. Access the UI on your browser using VM IP Address, example : 103.x.x.x:9001
