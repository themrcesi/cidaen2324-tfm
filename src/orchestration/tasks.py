from typing import Dict, List, Optional, Tuple
import datetime
import json
from prefect import task, get_run_logger
from prefect.tasks import task_input_hash
import time
import random
import boto3
from botocore.config import Config

ecs_client = boto3.client("ecs", region_name="eu-west-3")
lambda_client = boto3.client(
    "lambda", region_name="eu-west-3", config=Config(read_timeout=600)
)


def _get_task_status(cluster, task_arn) -> Tuple[str, int]:
    response = ecs_client.describe_tasks(cluster=cluster, tasks=[task_arn])
    task = response["tasks"][0]
    return task["lastStatus"], task.get("containers", [{}])[0].get("exitCode")


def _check_lambda_execution_status(response, lambda_function_name) -> Dict:
    response_payload = json.loads(response["Payload"].read())
    # Check for function errors
    if "FunctionError" in response:
        error_message = response_payload.get("errorMessage", "Unknown error")
        raise RuntimeError(
            f"Lambda function {lambda_function_name} failed with error: {error_message}"
        )
    return response_payload


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
    cache_expiration=datetime.timedelta(hours=3),
    retries=2,
    retry_delay_seconds=5,
)
def raw_categories(day: Optional[datetime.datetime] = None) -> Dict:
    """
    Retrieves raw category data for a given day.

    Args:
        day (Optional[datetime.datetime]): The day for which to retrieve the data. If not provided, the current day is used.

    Returns:
        Dict: A dictionary containing the raw category data.

    Raises:
        RuntimeError: If the lambda function "raw_download_categories" fails to execute.

    Notes:
        - The function is decorated with `@task` to indicate that it is a Prefect task.
        - The task is cached using the `cache_key_fn` and `cache_expiration` parameters.
        - The task is retried up to two times with a delay of 5 seconds between retries.
    """
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="raw_download_categories",
        InvocationType="RequestResponse",
        Payload=json.dumps({"day": day.isoformat()}),
    )
    response = _check_lambda_execution_status(result, "raw_download_categories")
    result = json.loads(response["body"])
    return result


@task(
    name="raw_product_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=3),
    retries=1,
    retry_delay_seconds=10,
)
def raw_product_category(
    *,
    day: Optional[datetime.datetime] = None,
    category_id: int,
    category_path_root: str,
    category_search_path: str,
) -> None:
    """
    Retrieves raw product category data for a given day and category.

    Args:
        day (Optional[datetime.datetime]): The day for which to retrieve the data. If not provided, the current day is used.
        category_id (int): The ID of the category.
        category_path_root (str): The root path of the category.
        category_search_path (str): The search path of the category.

    Returns:
        None

    Raises:
        RuntimeError: If the lambda function "raw_download_product_category" fails to execute.

    Notes:
        - The function is decorated with `@task` to indicate that it is a Prefect task.
        - The task is cached using the `cache_key_fn` and `cache_expiration` parameters.
        - The task is retried up to one time with a delay of 10 seconds between retries.
    """
    try:
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
    except RuntimeError as e:
        get_run_logger().error(
            f"There has been an error downloading category {category_id}: {e}"
        )


@task(
    name="bronze_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=3),
    retries=2,
    retry_delay_seconds=5,
)
def bronze_categories() -> List[Dict]:
    """
    Retrieves the bronze categories from the lambda function "bronze_categories".

    This function is decorated with `@task` to indicate that it is a Prefect task. The task is cached using the `cache_key_fn` and `cache_expiration` parameters. The task is retried up to two times with a delay of 5 seconds between retries.

    Returns:
        List[Dict]: A list of dictionaries representing the bronze categories.

    Raises:
        RuntimeError: If the lambda function "bronze_categories" fails to execute.
    """
    result = lambda_client.invoke(
        FunctionName="bronze_categories", InvocationType="RequestResponse"
    )
    response = _check_lambda_execution_status(result, "bronze_categories")
    categories = response["body"]
    return categories


@task(
    name="bronze_products",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(hours=1),
    retries=2,
    retry_delay_seconds=5,
)
def bronze_products(day: Optional[datetime.datetime] = None) -> None:
    """
    This function runs a Prefect task named "bronze_products" that triggers an AWS ECS task.

    It takes an optional parameter `day` of type `datetime.datetime`, defaulting to the current date and time if not provided.

    The function uses the `ecs_client` to run a task with the specified `task_definition_name` and `cluster_name`,
    overriding the container environment with the provided `day` parameter.

    It then checks the execution status of the ECS task using the `_check_ecs_task_execution_status` function.

    Returns:
        None
    """
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
    """
    Runs the "silver_products" task using AWS Lambda.

    This function is a Prefect task that triggers an AWS Lambda function named "silver_products".
    It takes an optional parameter `day` of type `datetime.datetime`, defaulting to the current date and time if not provided.

    The function invokes the Lambda function with the provided `day` parameter.
    It then checks the execution status of the Lambda function using the `_check_lambda_execution_status` function.

    Parameters:
        day (Optional[datetime.datetime]): The day for which to retrieve the silver products. If not provided, the current day is used.

    Returns:
        None

    Retries:
        - The task is retried up to two times with a delay of 5 seconds between retries.

    Caching:
        - The task is cached using the `cache_key_fn` and `cache_expiration` parameters.
        - The cache expires after 1 hour.
    """
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
    retry_delay_seconds=10,
)
def gold_categories(day: Optional[datetime.datetime] = None) -> None:
    """
    Runs the "gold_categories" task using AWS Lambda.

    This function is a Prefect task that triggers an AWS Lambda function named "gold_categories".
    It takes an optional parameter `day` of type `datetime.datetime`, defaulting to the current date and time if not provided.

    The function invokes the Lambda function with the provided `day` parameter.
    It then checks the execution status of the Lambda function using the `_check_lambda_execution_status` function.

    Parameters:
        day (Optional[datetime.datetime]): The day for which to retrieve the gold categories. If not provided, the current day is used.

    Returns:
        None

    Retries:
        - The task is retried up to two times with a delay of 5 seconds between retries.

    Caching:
        - The task is cached using the `cache_key_fn` and `cache_expiration` parameters.
        - The cache expires after 1 hour.
    """
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
    retries=1,
    retry_delay_seconds=60,
)
def gold_locations(day: Optional[datetime.datetime] = None) -> None:
    """
    Runs the "gold_locations" task using AWS Lambda.

    This function is a Prefect task that triggers an AWS Lambda function named "gold_locations".
    It takes an optional parameter `day` of type `datetime.datetime`, defaulting to the current date and time if not provided.

    The function invokes the Lambda function with the provided `day` parameter.
    It then checks the execution status of the Lambda function using the `_check_lambda_execution_status` function.

    Parameters:
        day (Optional[datetime.datetime]): The day for which to retrieve the gold locations. If not provided, the current day is used.

    Returns:
        None

    Retries:
        - The task is retried up to two times with a delay of 5 seconds between retries.

    Caching:
        - The task is cached using the `cache_key_fn` and `cache_expiration` parameters.
        - The cache expires after 1 hour.
    """
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
    retry_delay_seconds=10,
)
def gold_products(day: Optional[datetime.datetime] = None) -> None:
    """
    Runs the "gold_products" task using AWS Lambda.

    This function is a Prefect task that triggers an AWS Lambda function named "gold_products".
    It takes an optional parameter `day` of type `datetime.datetime`, defaulting to the current date and time if not provided.

    The function invokes the Lambda function with the provided `day` parameter.
    It then checks the execution status of the Lambda function using the `_check_lambda_execution_status` function.

    Parameters:
        day (Optional[datetime.datetime]): The day for which to retrieve the gold products. If not provided, the current day is used.

    Returns:
        None

    Retries:
        - The task is retried up to two times with a delay of 5 seconds between retries.

    Caching:
        - The task is cached using the `cache_key_fn` and `cache_expiration` parameters.
        - The cache expires after 1 hour.
    """
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
