import json
import datetime
from etl.raw import download_categories
from etl.utils import save_json_to_s3, S3_BUCKET_DATA, S3_BUCKET_RAW_CATEGORY_PATH


def lambda_handler(event, context):
    """
    AWS Lambda handler to download categories from the API.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object passed to the Lambda function.

    Returns:
        dict: A dictionary containing the downloaded categories.
    """
    day = (
        datetime.datetime.fromisoformat(inputt)
        if (inputt := event.get("day"))
        else datetime.datetime.today()
    )
    response = download_categories(day)
    save_json_to_s3(
        S3_BUCKET_DATA,
        f"{S3_BUCKET_RAW_CATEGORY_PATH}/{day.date().strftime('%Y-%m-%d')}.json",
        response,
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response),
    }
