import datetime

import awswrangler as wr
from etl.silver import products
from etl.utils import S3_BUCKET_SILVER_PRODUCTS_PATH, S3_BUCKET_DATA


def lambda_handler(event, context):
    day = (
        datetime.datetime.fromisoformat(inputt)
        if (inputt := event.get("day"))
        else datetime.datetime.today()
    )
    silver_products_df = products(day)
    wr.s3.to_parquet(
        df=silver_products_df,
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_SILVER_PRODUCTS_PATH}",
        dataset=True,
        partition_cols=["date"],
        mode="overwrite_partitions",
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
    }


if __name__ == "__main__":
    for day in ["2024-08-08", "2024-08-09", "2024-08-10", "2024-08-11", "2024-08-12"]:
        lambda_handler({"day": day}, {})
