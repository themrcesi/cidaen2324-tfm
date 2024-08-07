from .flows import etl
from prefect.deployments import DeploymentImage

if __name__ == "__main__":
    etl.deploy(
        name="test-deployment",
        work_pool_name="cidaen-tfm-ecs-pool",
        image=DeploymentImage(
            name="prefect-flows:cidaen-tfm-etl",
            platform="LINUX/ARM64",
        ),
        job_variables={
            "env": {"EXTRA_PIP_PACKAGES": "boto3"},
            "task_definition_arn": "arn:aws:ecs:eu-west-3:480361390441:task-definition/prefect-cidaen-etl:1",
        },
    )
# auto aprovisionar infraestructura
# crear una task definition previa
# cambiar arn en deployment
# ci deployment
