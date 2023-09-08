# Minio

## Installation Using Docker-Compose

1. Install Docker Compose

    ```bash
    sudo apt install docker-compose
    sudo apt-mark hold docker-compose
    ```

2. Clone or download minio-compose.yaml from repository/ftp server if you don't have it yet

3. Execute minio installation

    ```bash
    docker compose -f minio-compose.yaml up -d
    ```

4. Access the UI on your browser using VM IP Address, example : 103.x.x.x:9001

## Create bucket in MinIO
