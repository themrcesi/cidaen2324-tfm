from typing import Optional
import datetime
import boto3
import json
from constants import S3_BUCKET_DATA

s3_client = boto3.client("s3")
lambda_client = boto3.client(
    "lambda",
    region_name="us-east-1",
)


def raw_categories(day: Optional[datetime.datetime] = None):
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="raw_download_categories",
        InvocationType="RequestResponse",
        Payload=json.dumps({"day": day.isoformat()}),
    )
    result = json.loads(result["Payload"].read())["body"]
    s3_client.put_object(
        Bucket=S3_BUCKET_DATA,
        Key="raw/categories/{day}.json".format(day=day.isoformat()),
        Body=json.dumps(result),
        ContentType="application/json",
    )


def raw_product_category(
    *, day: Optional[datetime.datetime] = None, category_id: int, category_path: str
):
    day = day or datetime.datetime.now()
    result = lambda_client.invoke(
        FunctionName="raw_download_product_category",
        InvocationType="RequestResponse",
        Payload=json.dumps(
            {
                "day": day.isoformat(),
                "category_id": category_id,
                "category_path": category_path,
            }
        ),
    )
    result = json.loads(result["Payload"].read())["body"]
    s3_client.put_object(
        Bucket=S3_BUCKET_DATA,
        Key="raw/products_category/{category_id}/{day}.json".format(
            day=day.isoformat(), category_id=category_id
        ),
        Body=json.dumps(result),
        ContentType="application/json",
    )


if __name__ == "__main__":
    # raw_categories()
    raw_product_category(category_id=100, category_path="cars")
