from typing import Dict, List, Optional, Tuple
import datetime
import boto3
import json
from prefect import task
from prefect.tasks import task_input_hash
import time
import random


lambda_client = boto3.client(
    "lambda",
    region_name="eu-west-3",
)
ecs_client = boto3.client("ecs", region_name="eu-west-3")


def _get_task_status(cluster, task_arn) -> Tuple[str, int]:
    response = ecs_client.describe_tasks(cluster=cluster, tasks=[task_arn])
    task = response["tasks"][0]
    return task["lastStatus"], task.get("containers", [{}])[0].get("exitCode")


def _check_lambda_execution_status(response, lambda_function_name) -> None:
    response_payload = json.loads(response["Payload"].read())
    # Check for function errors
    if "FunctionError" in response:
        error_message = response_payload.get("errorMessage", "Unknown error")
        raise RuntimeError(
            f"Lambda function {lambda_function_name} failed with error: {error_message}"
        )


def _check_ecs_task_execution_status(cluster_name, response):
    task_arn = response["tasks"][0]["taskArn"]
    while True:
        status, exit_code = _get_task_status(cluster_name, task_arn)
        print(f"Current status: {status}")

        if status in ["SUCCEEDED", "FAILED", "STOPPED"]:
            break
        time.sleep(10)  # Wait for 10 seconds before checking again

    # Raise an error if the task failed
    if status == "FAILED" or (exit_code is not None and exit_code != 0):
        raise RuntimeError(f"Task {task_arn} failed with exit code {exit_code}")


@task(
    name="raw_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def raw_categories(day: Optional[datetime.datetime] = None) -> Dict:
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="raw_download_categories",
        InvocationType="RequestResponse",
        Payload=json.dumps({"day": day.isoformat()}),
    )
    _check_lambda_execution_status(result, "raw_download_categories")
    result = json.loads(json.loads(result["Payload"].read())["body"])
    return result


@task(
    name="raw_product_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def raw_product_category(
    *,
    day: Optional[datetime.datetime] = None,
    category_id: int,
    category_path_root: str,
    category_search_path: str,
) -> None:
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="raw_download_product_category",
        InvocationType="RequestResponse",
        Payload=json.dumps(
            {
                "day": day.isoformat(),
                "category_id": category_id,
                "category_path_root": category_path_root,
                "category_search_path": category_search_path,
            }
        ),
    )
    _check_lambda_execution_status(result, "raw_download_product_category")
    time.sleep(random.random() * 2)


@task(
    name="bronze_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def bronze_categories() -> List[Dict]:
    result = lambda_client.invoke(
        FunctionName="bronze_categories", InvocationType="RequestResponse"
    )
    _check_lambda_execution_status(result, "bronze_categories")
    categories = json.loads(result["Payload"].read())["body"]
    return categories


@task(
    name="bronze_products",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def bronze_products(day: Optional[datetime.datetime] = None) -> None:
    day = day or datetime.datetime.now()
    task_definition_name = "bronze_products"
    cluster_name = "cidaen-tfm-etl"
    network_configuration = {
        "awsvpcConfiguration": {
            "securityGroups": ["sg-d252f7ab"],
            "subnets": [
                "subnet-9bb9b7e0",
                "subnet-c27681aa",
                "subnet-b3c390fe",
            ],
            "assignPublicIp": "ENABLED",
        }
    }
    container_overrides = [
        {
            "name": "bronze_products",
            "environment": [{"name": "day", "value": day.strftime("%Y-%m-%d")}],
        },
    ]
    response = ecs_client.run_task(
        cluster=cluster_name,
        networkConfiguration=network_configuration,
        taskDefinition=task_definition_name,
        launchType="FARGATE",
        overrides={"containerOverrides": container_overrides},
        count=1,
    )
    _check_ecs_task_execution_status(cluster_name, response)


@task(
    name="silver_products",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def silver_products(day: Optional[datetime.datetime] = None) -> None:
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="silver_products",
        InvocationType="RequestResponse",
        Payload=json.dumps({"day": day.isoformat()}),
    )
    _check_lambda_execution_status(result, "silver_products")


@task(
    name="gold_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def gold_categories(day: Optional[datetime.datetime] = None) -> None:
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="gold_categories",
        InvocationType="RequestResponse",
        Payload=json.dumps({"day": day.isoformat()}),
    )
    _check_lambda_execution_status(result, "gold_categories")


@task(
    name="gold_locations",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def gold_locations(day: Optional[datetime.datetime] = None) -> None:
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="gold_locations",
        InvocationType="RequestResponse",
        Payload=json.dumps({"day": day.isoformat()}),
    )
    _check_lambda_execution_status(result, "gold_locations")


@task(
    name="gold_products",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def gold_products(day: Optional[datetime.datetime] = None) -> None:
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="gold_products",
        InvocationType="RequestResponse",
        Payload=json.dumps({"day": day.isoformat()}),
    )
    _check_lambda_execution_status(result, "gold_products")


if __name__ == "__main__":
    raw_categories()
    # raw_product_category(category_id=100, category_path="cars")
