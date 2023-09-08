# Label Studio

## Installation

1. Clone or download label_studio-compose.yaml from repository/ftp server if you don't have it yet

2. Execute label studio installation

    ```bash
    docker compose -f label_studio-compose.yaml up -d
    ```

## Label Studio and MinIO integration

1. Make sure that minio and label studio is installed already

2. Make a new project in label studio

3. Navigate to settings section

4. In the cloud storage section, Add installed minio as storage source

5. Choose add source storage

6. Select S3 type storage with following details

    - Bucket name: **bucket-name**
    - S3 endpoit: **a.b.c.d:9000**
    - Access key id: **minioadmin**
    - Secret Access key: **minioadmin**
    - Treat every bucket object as a source file : **ON**

7. Verify connection with **Check Connection** button

8. Click **Add Storage** if connection successfully established
