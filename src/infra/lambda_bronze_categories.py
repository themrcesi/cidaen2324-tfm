import awswrangler as wr
from etl.bronze import categories
from etl.utils import S3_BUCKET_BRONZE_CATEGORIES_PATH, S3_BUCKET_DATA


def lambda_handler(event, context):
    """
    Lambda function handler that executes the ETL process for the bronze categories.
    Args:
        event (dict): The event data passed to the Lambda function.
        context (object): The runtime information of the Lambda function.
    Returns:
        pandas.DataFrame: The resulting DataFrame containing the bronze categories.
    This function retrieves the bronze categories by calling the `bronze_categories` function from the `etl.bronze` module.
    It then saves the DataFrame to a Parquet file in the specified S3 bucket path.
    The function returns the resulting DataFrame.
    """
    bronze_categories_df = categories()
    wr.s3.to_parquet(
        bronze_categories_df,
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_BRONZE_CATEGORIES_PATH}/",
        mode="overwrite",
        dataset=True,
    )
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": bronze_categories_df.to_dict(orient="records"),
    }


if __name__ == "__main__":
    lambda_handler(None, None)
