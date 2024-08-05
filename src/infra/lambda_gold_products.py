import datetime

import awswrangler as wr
from etl.gold import gold_product
from etl.utils import S3_BUCKET_DATA, S3_BUCKET_GOLD_PRODUCTS_PATH


def lambda_handler(event, context):
    day = (
        datetime.datetime.fromisoformat(inputt)
        if (inputt := event.get("day"))
        else datetime.datetime.today()
    )
    gold_df = gold_product(day)
    wr.s3.to_csv(
        df=gold_df,
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_GOLD_PRODUCTS_PATH}",
        index=False,
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
    }


if __name__ == "__main__":
    lambda_handler({"day": "2024-07-29"}, {})
