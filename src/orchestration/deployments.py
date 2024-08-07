from .flows import etl
from prefect.deployments.runner import DeploymentImage
from ..constants import ECS_PREFECT_ETL_PIPELINE_TASK_DEFINITION_ARN

if __name__ == "__main__":
    _ = etl.deploy(
        name="tfm-etl-pipeline",
        work_pool_name="cidaen-tfm-etl-pipeline",
        image=DeploymentImage(
            name="tfm-etl-pipeline:latest",
            platform="LINUX/ARM64",
        ),
        job_variables={
            "env": {"EXTRA_PIP_PACKAGES": "boto3 prefect-aws"},
            "task_definition_arn": ECS_PREFECT_ETL_PIPELINE_TASK_DEFINITION_ARN,
        },
        cron="0 5 * * *",
    )
