# RabbitMQ

> Plan to do single install on master node, so that all worker nodes just have to connect to this rabbitmq cluster with different exchanges.

## Installation

1. **Install the RabbitMQ Cluster Operator**

    ```bash
    kubectl apply -f "https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"
    ```

2. Create a RabbitMQ cluster with custom `.yaml` and modify the values according to your needs. You can find examples here [https://github.com/rabbitmq/cluster-operator/tree/main/docs/examples/](https://github.com/rabbitmq/cluster-operator/tree/main/docs/examples/)

    ```yaml
    apiVersion: rabbitmq.com/v1beta1
    kind: RabbitmqCluster
    metadata:
        name: rabbitmq-basic
    spec:
      replicas: 1
      resources:
        requests:
          cpu: 500m
          memory: 1Gi
        limits:
          cpu: 800m
          memory: 1Gi
    ```

3. Apply the cluster

    ```bash
    kubectl apply -f <PATH>
    ```

4. After the pod is running get the credentials for rabbitmq

    ```bash
    username="$(kubectl get secret rabbitmq-basic-default-user -o jsonpath='{.data.username}' | base64 --decode)"
    password="$(kubectl get secret rabbitmq-basic-default-user -o jsonpath='{.data.password}' | base64 --decode)"
    echo username
    echo password
    ```

5. Port forward the service

    ```bash
    kubectl port-forward "service/rabbitmq-basic" 15672:15672 --address=0.0.0.0
    kubectl port-forward "service/rabbitmq-basic" 5672:5672 --address=0.0.0.0
    ```

6. Login to the dashboard at port `15672` and create a new user for use in application

    ![Create New User](rabbitmq-assets/create-new-user.png)

7. Give the user virtual host permission

    ![Virtual Host Permission](rabbitmq-assets/virtual-host-permission.png)

8. Now you can use this user and port `5672` for connection (using `pika` in Python for example)
