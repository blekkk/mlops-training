import uuid
import kfp.components as comp
from kfp import dsl
from kfp.components import InputPath, InputTextFile, OutputPath, OutputTextFile
from kfp.onprem import mount_pvc
from typing import Dict, List


def download_and_unzip_data(
    minio_host: str,
    minio_access: str,
    minio_secret: str,
    body_dict: dict,
    uuid: str,
):
    from minio import Minio
    from minio.error import S3Error
    from zipfile import ZipFile
    import os

    minio_bucket = body_dict["Records"][0]["s3"]["bucket"]["name"]
    minio_object = body_dict["Key"].replace(minio_bucket, "")
    local_file = body_dict["Key"]

    try:
        client = Minio(
            minio_host,
            access_key=minio_access,
            secret_key=minio_secret,
            secure=False,
        )

        client.fget_object(
            minio_bucket,
            minio_object,
            local_file,
        )
    except S3Error as exc:
        print("error occurred.", exc)

    with ZipFile(
        local_file,
        "r",
    ) as zObject:
        zObject.extractall(path=f"/mnt/{uuid}/dataset")


def slice_data(uuid: str):
    import os

    # os.system("apt-get update && apt-get install ffmpeg libsm6 libxext6  -y")

    from sahi.slicing import slice_coco
    import shutil

    COCO_ANNOTATION_FILE = f"/mnt/{uuid}/dataset/result.json"
    SLICED_COCO_ANNOTATION_FILE_NAME = "sliced"
    SLICED_COCO_IMAGE_DIR = f"/mnt/{uuid}/dataset/"
    SLICED_COCO_OUTPUT_DIR = f"/mnt/{uuid}/coco-sliced"

    coco_dict, coco_path = slice_coco(
        coco_annotation_file_path=COCO_ANNOTATION_FILE,
        output_coco_annotation_file_name=SLICED_COCO_ANNOTATION_FILE_NAME,
        image_dir=SLICED_COCO_IMAGE_DIR,
        output_dir=SLICED_COCO_OUTPUT_DIR,
        slice_height=512,
        slice_width=512,
        overlap_height_ratio=0.125,
        overlap_width_ratio=0.125,
        ignore_negative_samples=False,
        verbose=True,
    )

    os.system(f"rm -rf /mnt/{uuid}/dataset")


def convert_coco_to_yolo(uuid: str):
    import os
    import shutil
    import supervision as sv

    COCO_IMAGE_DIR = f"/mnt/{uuid}/coco-sliced"
    COCO_ANNOTATION_PATH = f"/mnt/{uuid}/coco-sliced/sliced_coco.json"
    YOLO_IMAGE_DIR = f"/mnt/{uuid}/yolo/data"
    YOLO_ANNOTATION_DIR = f"/mnt/{uuid}/yolo/data"
    YOLO_YAML_PATH = f"/mnt/{uuid}/yolo/data.yaml"

    ds = sv.DetectionDataset.from_coco(
        images_directory_path=COCO_IMAGE_DIR,
        annotations_path=COCO_ANNOTATION_PATH,
    ).as_yolo(
        images_directory_path=YOLO_IMAGE_DIR,
        annotations_directory_path=YOLO_ANNOTATION_DIR,
        data_yaml_path=YOLO_YAML_PATH,
    )

    os.system(f"rm -rf /mnt/{uuid}/coco-sliced")


def split_dataset(uuid: str):
    import os
    import random
    import shutil as sh
    from pathlib import Path

    def split_dataset_file_from_images(path, output_dir, val_ratio=0.1):
        DATA_DIR = Path(path)
        img_list = list((DATA_DIR.glob("*.jpg")))
        random.shuffle(img_list)
        os.makedirs(f"{output_dir}/val", exist_ok=True)
        os.makedirs(f"{output_dir}/train", exist_ok=True)

        for i in range(0, int(len(img_list) * val_ratio)):
            val_img = img_list.pop()
            sh.move(
                f"{DATA_DIR}/{val_img.stem}.jpg", f"{output_dir}/val/{val_img.stem}.jpg"
            )
            sh.move(
                f"{DATA_DIR}/{val_img.stem}.txt", f"{output_dir}/val/{val_img.stem}.txt"
            )

        for img in img_list:
            sh.move(f"{DATA_DIR}/{img.stem}.jpg", f"{output_dir}/train/{img.stem}.jpg")
            sh.move(f"{DATA_DIR}/{img.stem}.txt", f"{output_dir}/train/{img.stem}.txt")

    YOLO_DATA_DIR = f"/mnt/{uuid}/yolo/data"
    YOLO_SPLITTED_DATA_DIR = f"/mnt/{uuid}/yolo"

    split_dataset_file_from_images(YOLO_DATA_DIR, YOLO_SPLITTED_DATA_DIR)

    CONFIG = [f"\ntrain: /mnt/{uuid}/yolo/train", f"\nval: /mnt/{uuid}/yolo/val"]

    with open(f"/mnt/{uuid}/yolo/data.yaml", "a") as f:
        for line in CONFIG:
            f.write(line)


def train_model(uuid: str, host_ip: str):
    from ultralytics import YOLO
    import mlflow
    import os
    import re
    from pathlib import Path
    from ultralytics.utils import LOGGER, SETTINGS, TESTS_RUNNING, colorstr

    global run_id, experiment_name

    os.environ["MLFLOW_TRACKING_URI"] = f"http://{host_ip}:5000"
    os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = f"http://{host_ip}:9000"
    os.environ["MLFLOW_S3_IGNORE_TLS"] = "true"
    mlflow_location = os.environ["MLFLOW_TRACKING_URI"]

    mlflow.set_tracking_uri(mlflow_location)
    experiment_name = "/Shared/YOLOv8"

    def on_pretrain_routine_end(trainer):
        """Logs training parameters to MLflow."""
        run_name = trainer.args.name
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            mlflow.create_experiment(experiment_name)
        mlflow.set_experiment(experiment_name)
        experiment = mlflow.get_experiment_by_name(experiment_name)

        prefix = colorstr("MLFlow: ")
        try:
            active_run = mlflow.active_run()
            if not active_run:
                active_run = mlflow.start_run(
                    experiment_id=experiment.experiment_id, run_name=run_name
                )
            run_id = active_run.info.run_id
            LOGGER.info(f"{prefix}Using run_id({run_id}) at {mlflow_location}")
            mlflow.log_params(vars(trainer.model.args))
        except Exception as err:
            LOGGER.error(f"{prefix}Failing init - {repr(err)}")
            LOGGER.warning(f"{prefix}Continuing without Mlflow")

    def on_fit_epoch_end(trainer):
        """Logs training metrics to Mlflow."""
        if mlflow:
            metrics_dict = {
                f"{re.sub('[()]', '', k)}": float(v) for k, v in trainer.metrics.items()
            }
            mlflow.log_metrics(metrics=metrics_dict, step=trainer.epoch)

    def on_train_end(trainer):
        """Called at end of train loop to log model artifact info."""
        if mlflow:
            mlflow.log_artifact(trainer.last)
            mlflow.log_artifact(trainer.best)
            mlflow.pyfunc.log_model(
                artifact_path=run_id,
                artifacts={"model_path": str(trainer.save_dir)},
                python_model=mlflow.pyfunc.PythonModel(),
            )

    model = YOLO("yolov8n-seg.pt")
    model.add_callback("on_pretrain_routine_end", on_pretrain_routine_end)
    model.add_callback("on_fit_epoch_end", on_fit_epoch_end)
    model.add_callback("on_train_end", on_train_end)

    model.train(data=f"/mnt/{uuid}/yolo/data.yaml", epochs=15, imgsz=512)

    os.system(f"rm -rf /mnt/{uuid}/")


download_and_unzip_data_op = comp.create_component_from_func(
    download_and_unzip_data, packages_to_install=["minio==7.1.15"]
)
slice_data_op = comp.create_component_from_func(
    slice_data,
    packages_to_install=["sahi==0.11.14"],
    base_image="hdgigante/python-opencv:4.7.0-debian",
)
convert_coco_to_yolo_op = comp.create_component_from_func(
    convert_coco_to_yolo,
    packages_to_install=["supervision==0.12.0"],
    base_image="python:3.10",
)
split_dataset_op = comp.create_component_from_func(split_dataset)
train_model_op = comp.create_component_from_func(
    train_model,
    packages_to_install=["mlflow==2.4.2", "boto3==1.28.18"],
    base_image="blekkk/yolo-runtime:1.0.0",
)


@dsl.pipeline()
def yolo_pipeline(
    minio_host: str, minio_access: str, minio_secret: str, host_ip: str, body_dict: dict
):
    run_uuid = uuid.uuid4()
    run_uuid = str(run_uuid)

    def mount_pvc_func():
        return mount_pvc(
            pvc_name="kubeflow-pipeline",
            volume_name="kubeflow-pipeline",
            volume_mount_path="/mnt",
        )

    download_and_unzip_data_task = download_and_unzip_data_op(
        minio_host=minio_host,
        minio_access=minio_access,
        minio_secret=minio_secret,
        body_dict=body_dict,
        uuid=run_uuid,
    )
    slice_data_task = slice_data_op(uuid=run_uuid).after(download_and_unzip_data_task)
    convert_coco_to_yolo_task = convert_coco_to_yolo_op(uuid=run_uuid).after(
        slice_data_task
    )
    split_dataset_task = split_dataset_op(uuid=run_uuid).after(
        convert_coco_to_yolo_task
    )
    train_model_task = train_model_op(uuid=run_uuid, host_ip=host_ip).after(split_dataset_task)

    download_and_unzip_data_task.apply(mount_pvc_func())
    slice_data_task.apply(mount_pvc_func())
    convert_coco_to_yolo_task.apply(mount_pvc_func())
    split_dataset_task.apply(mount_pvc_func())
    train_model_task.set_gpu_limit(gpu="1", vendor="nvidia").apply(mount_pvc_func())


@dsl.pipeline()
def yolo_pipeline(
    minio_host: str, minio_access: str, minio_secret: str, host_ip: str, body_dict: dict
):
    run_uuid = uuid.uuid4()
    run_uuid = str(run_uuid)

    def mount_pvc_func():
        return mount_pvc(
            pvc_name="kubeflow-pipeline",
            volume_name="kubeflow-pipeline",
            volume_mount_path="/mnt",
        )

    download_and_unzip_data_task = download_and_unzip_data_op(
        minio_host=minio_host,
        minio_access=minio_access,
        minio_secret=minio_secret,
        body_dict=body_dict,
        uuid=run_uuid,
    )
    slice_data_task = slice_data_op(uuid=run_uuid).after(download_and_unzip_data_task)
    convert_coco_to_yolo_task = convert_coco_to_yolo_op(uuid=run_uuid).after(
        slice_data_task
    )
    split_dataset_task = split_dataset_op(uuid=run_uuid).after(
        convert_coco_to_yolo_task
    )
    train_model_task = train_model_op(uuid=run_uuid, host_ip=host_ip).after(split_dataset_task)

    download_and_unzip_data_task.apply(mount_pvc_func())
    slice_data_task.apply(mount_pvc_func())
    convert_coco_to_yolo_task.apply(mount_pvc_func())
    split_dataset_task.apply(mount_pvc_func())
    train_model_task.set_gpu_limit(gpu="1", vendor="nvidia").apply(mount_pvc_func())
