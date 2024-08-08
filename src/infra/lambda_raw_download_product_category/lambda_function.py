import datetime
import asyncio
from etl.raw import download_products_by_category
from etl.utils import (
    MAX_PRODUCTS,
    S3_BUCKET_DATA,
    save_json_to_s3,
    S3_BUCKET_RAW_PRODUCTS_CATEGORY_PATH,
)
import logging


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
    day = (
        datetime.datetime.fromisoformat(inputt)
        if (inputt := event.get("day"))
        else datetime.datetime.today()
    )
    category_id = event["category_id"]
    category_path_root = event["category_path_root"]
    category_search_path = event["category_search_path"]
    max_products = event.get("max_products", MAX_PRODUCTS)
    logging.info(f"Downloading products for category {category_id} on {day.date()}")
    result = asyncio.run(
        download_products_by_category(
            day,
            category_id=category_id,
            category_path_root=category_path_root,
            category_search_path=category_search_path,
            max_products=max_products,
        )
    )
    logging.info(
        f"Downloaded {len(result['search_objects'])} products for category {category_id} on {day.date()} and saving to S3 in {S3_BUCKET_RAW_PRODUCTS_CATEGORY_PATH.format(day=day.date().strftime('%Y-%m-%d'))}/{category_id}.json"
    )
    save_json_to_s3(
        S3_BUCKET_DATA,
        f"{S3_BUCKET_RAW_PRODUCTS_CATEGORY_PATH.format(day=day.date().strftime('%Y-%m-%d'))}/{category_id}.json",
        result,
    )
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}}


if __name__ == "__main__":
    lambda_handler(
        {
            "day": datetime.datetime.now().isoformat(),
            "category_id": 10393,
            "category_path_root": "general",
            "category_search_path": "category_ids=13200&object_type_ids=10393",
        },
        {},
    )
