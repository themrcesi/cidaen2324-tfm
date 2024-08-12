import datetime

import awswrangler as wr
from etl.gold import gold_category_and_total
from etl.utils import S3_BUCKET_DATA, S3_BUCKET_GOLD_CATEGORIES_PATH


def lambda_handler(event, context):
    """
    This function is the entry point for an AWS Lambda function that retrieves gold categories for a given day and saves them to an S3 bucket.

    Parameters:
        event (dict): The event data passed to the Lambda function. It should contain a "day" key with a string value representing the day in ISO format.
        context (object): The runtime information of the Lambda function.

    Returns:
        dict: A dictionary with a "statusCode" key set to 200 and a "headers" key with a dictionary containing the "Content-Type" header set to "application/json".

    Raises:
        None

    Description:
        This function retrieves the day from the event data or uses the current date if no day is provided. It then calls the `gold_category_and_total` function to retrieve the gold categories for the given day. The retrieved data is saved to an S3 bucket using the `wr.s3.to_csv` function. Finally, the function returns a dictionary with the "statusCode" and "headers" keys.
    """
    day = (
        datetime.datetime.fromisoformat(inputt)
        if (inputt := event.get("day"))
        else datetime.datetime.today()
    )
    gold_categories = gold_category_and_total(day)
    wr.s3.to_csv(
        df=gold_categories,
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_GOLD_CATEGORIES_PATH}",
        index=False,
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
    }


if __name__ == "__main__":
    lambda_handler({"day": "2024-08-12"}, {})
