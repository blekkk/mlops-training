# MLFlow
MLFlow is an open source platform for managing the end-to-end machine learning lifecycle. It has the following features:

1. Tracking experiments: MLFlow allows you to track experiments and compare multiple runs to see which models perform the best.
2. Packaging code: MLFlow allows you to package your code and models, making it easy to reproduce and share your work.
3. Managing models: MLFlow makes it easy to deploy, manage, and serve machine learning models.
4. Collaboration: MLFlow enables collaboration between team members, making it easier to share knowledge and work together on projects.
5. extensibility: MLFlow is extensible and can be integrated with other tools and frameworks.

### Use Case
- A team of data scientists uses MLflow Tracking to record parameters and metrics from their experiments on a single problem domain. They use the MLflow UI to compare results and guide their exploration of the solution space. They store the outputs of their runs as MLflow models.
- An MLOps engineer uses the MLflow UI to compare the performance of different models and selects the best one for deployment. They register the model in the MLflow Registry to track this specific version’s performance in production.
- An MLOps engineer uses MLflow models to deploy a model to a production environment. They use MLflow Registry to track the model’s performance and to compare it to other models in production.
- A data scientist beginning work with a new project structures their code as an MLflow Project so that they can easily share it with others and run it with different parameters.

Overall, MLFlow provides a comprehensive solution for managing the machine learning lifecycle, from experimentation to deployment.
## Installation

1. Make sure docker is installed properly

2. Move to configuration files directory

    ```bash
    cd /home/len/installation/config-files/mlflow
    ```

3. Change values inside `.env` file
    - `MLFLOW_S3_ENDPOINT_URL`is your Minio API endpoint 
    - `MLFLOW_TRACKING_URI` is MLFlow endpoint

4. Apply deployments

    ```bash
    docker-compose --env-file .env -f compose.yaml up -d
    ```

5. Try access the dashboard at https://{IP}:5000/
