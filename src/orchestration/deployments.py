from .flows import etl
from prefect.deployments.runner import DeploymentImage

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
            "task_definition_arn": "arn:aws:ecs:eu-west-3:480361390441:task-definition/tfm-etl-pipeline:2",
        },
        cron="0 5 * * *",
    )
