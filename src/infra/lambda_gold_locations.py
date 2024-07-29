import datetime

import awswrangler as wr
from etl.gold import gold_location_and_total
from etl.utils import S3_BUCKET_DATA, S3_BUCKET_GOLD_LOCATIONS_PATH


def lambda_handler(event, context):
    day = (
        datetime.datetime.fromisoformat(inputt)
        if (inputt := event.get("day"))
        else datetime.datetime.today()
    )
    gold_locations = gold_location_and_total(day)
    wr.s3.to_csv(
        df=gold_locations,
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_GOLD_LOCATIONS_PATH}",
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
    }


if __name__ == "__main__":
    lambda_handler({"day": "2024-07-29"}, {})
