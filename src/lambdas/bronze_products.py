import datetime

import awswrangler as wr
from ..etl.bronze import products
from ..etl.utils import S3_BUCKET_BRONZE_PRODUCTS_PATH, S3_BUCKET_DATA


def lambda_handler(event, context):
    """
    Lambda function that handles the event and context for processing bronze products.

    Args:
        event (dict): The event data passed to the Lambda function.
            day (str, optional): The date of the data to process in ISO format (YYYY-MM-DD).
                If not provided, the current date is used.
        context (object): The context object containing information about the Lambda function execution environment.

    Returns:
        dict: A dictionary containing the response status code and headers.
            statusCode (int): The HTTP status code for the response.
            headers (dict): The headers for the response.
                Content-Type (str): The content type of the response.

    Note:
        This function retrieves the bronze products data using the `products` function from the `etl.bronze` module.
        The data is then saved to S3 using the `wr.s3.to_parquet` function from the `awswrangler` module.
        The data is saved in the specified S3 bucket and partitioned by the 'date' column.
    """
    day = (
        datetime.datetime.fromisoformat(inputt)
        if (inputt := event.get("day"))
        else datetime.datetime.today()
    )
    bronze_products_df = products(day)
    wr.s3.to_parquet(
        df=bronze_products_df,
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_BRONZE_PRODUCTS_PATH}",
        dataset=True,
        partition_cols=["date"],
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
    }


if __name__ == "__main__":
    lambda_handler({}, {})
