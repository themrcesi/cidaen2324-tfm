import json
import datetime
from etl.raw import download_categories


def lambda_handler(event, context):
    """
    AWS Lambda handler to download categories from the API.

    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The context object passed to the Lambda function.

    Returns:
        dict: A dictionary containing the downloaded categories.
    """
    day = datetime.datetime.fromisoformat(event["day"])
    response = download_categories(day)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response),
    }
