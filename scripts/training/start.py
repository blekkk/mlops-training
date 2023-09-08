import kfp
from minio import Minio
from minio.error import S3Error
from ast import literal_eval
from kubeflow.pipelinev import yolo_pipeline
from kubeflow.auth import get_istio_auth_session
import socket
import pika
import sys
import os
import subprocess
import argparse

parser = argparse.ArgumentParser(
    description="Training script",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "--yolo-only",
    action="store_true",
    help="Run training script without preprocessing",
    required=False,
)

args = parser.parse_args()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
HOST_IP = s.getsockname()[0]
s.close()

MINIO_HOST = os.environ.get("MINIO_HOST") or f"{HOST_IP}:9000"
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY") or "minioadmin"
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY") or "minioadmin"

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST") or HOST_IP
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT") or "5672"
RABBITMQ_EXCHANGE = os.environ.get("RABBITMQ_EXCHANGE") or "mlops"
RABBITMQ_USER = os.environ.get("RABBITMQ_USER") or "useradmin"
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_PASSWORD") or "useradmin"

KUBEFLOW_ENDPOINT = os.environ.get("KUBEFLOW_ENDPOINT") or f"http://{HOST_IP}:8087"
KUBEFLOW_USERNAME = os.environ.get("KUBEFLOW_USERNAME") or "user@example.com"
KUBEFLOW_PASSWORD = os.environ.get("KUBEFLOW_PASSWORD") or "12341234"

auth_session = get_istio_auth_session(
    url=KUBEFLOW_ENDPOINT, username=KUBEFLOW_USERNAME, password=KUBEFLOW_PASSWORD
)

kfp_client = kfp.Client(
    host=f"{KUBEFLOW_ENDPOINT}/pipeline", cookies=auth_session["session_cookie"]
)


def minio_client():
    return Minio(
        MINIO_HOST,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )


def pika_callback(ch, method, properties, body):
    body_dict = literal_eval(body.decode("utf-8"))

    print("Received message:")
    print(body.decode("utf-8"))

    pipeline_params = {
        "minio": {
            "minio_host": MINIO_HOST,
            "minio_access": MINIO_ACCESS_KEY,
            "minio_secret": MINIO_SECRET_KEY,
            "body_dict": body_dict,
        }
    }

    kfp_client.create_run_from_pipeline_func(
        yolo_pipeline,
        arguments={
            "minio_host": MINIO_HOST,
            "minio_access": MINIO_ACCESS_KEY,
            "minio_secret": MINIO_SECRET_KEY,
            "host_ip": HOST_IP,
            "body_dict": body_dict,
        },
        namespace="kubeflow-user-example-com",
        experiment_name="Default",
    )


def pika_start():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=30,
        )
    )

    channel = connection.channel()

    channel.exchange_declare(exchange=RABBITMQ_EXCHANGE, exchange_type="fanout")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=queue_name)

    print("🐍 is listening for messages. To exit press CTRL+C")

    channel.basic_consume(
        queue=queue_name, on_message_callback=pika_callback, auto_ack=True
    )

    channel.start_consuming()


try:
    client = minio_client()
    pika_start()
except S3Error as exc:
    print("error occurred.", exc)
