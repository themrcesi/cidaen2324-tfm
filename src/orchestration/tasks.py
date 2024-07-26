from typing import Dict, List, Optional
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


@task(
    name="raw_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(minutes=1),
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
    result = json.loads(json.loads(result["Payload"].read())["body"])
    return result


@task(
    name="raw_product_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(minutes=1),
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
    lambda_client.invoke(
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
    time.sleep(random.random() * 2)


@task(
    name="bronze_categories",
    cache_key_fn=task_input_hash,
    cache_expiration=datetime.timedelta(minutes=1),
    retries=2,
    retry_delay_seconds=5,
)
def bronze_categories() -> List[Dict]:
    result = lambda_client.invoke(
        FunctionName="bronze_categories", InvocationType="RequestResponse"
    )
    categories = json.loads(result["Payload"].read())["body"]
    return categories


if __name__ == "__main__":
    raw_categories()
    # raw_product_category(category_id=100, category_path="cars")
