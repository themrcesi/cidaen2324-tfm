import datetime
import json

from etl.raw import download_products_by_category
from etl.utils import RECURSION_LIMIT


def lambda_handler(event, context):
    """
    AWS Lambda handler to download products from a given category.

    Args:
        event (dict): The event data passed to the Lambda function.
            day (str): The date of the download in ISO format (YYYY-MM-DD).
            category_id (int): The ID of the category to download products from.
            category_path (str): The path of the category on the Wallapop API.
            recursion_limit (int, optional): The maximum number of recursive requests to make. Defaults to RECURSION_LIMIT.

    Returns:
        dict: A dictionary containing the downloaded search objects and the date of the download.

    Example:
        >>> lambda_handler({"day": "2022-01-01", "category_id": 123, "category_path": "path/to/category", "recursion_limit": 10000})
        {'search_objects': [...], 'date': '2022-01-01'}
    """
    day = datetime.datetime.fromisoformat(event["day"])
    category_id = event["category_id"]
    category_path = event["category_path"]
    recursion_limit = event.get("recursion_limit", RECURSION_LIMIT)
    result = download_products_by_category(
        day, category_id, category_path, recursion_limit
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }
