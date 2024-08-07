import datetime
from typing import Optional

from prefect import flow
from prefect_aws.s3 import S3Bucket

from .tasks import (
    bronze_categories,
    bronze_products,
    gold_categories,
    gold_locations,
    gold_products,
    raw_categories,
    raw_product_category,
    silver_products,
)

s3_bucket_block = S3Bucket.load("cidaen-tfm-prefect-results")


@flow(name="etl-tfm", result_storage=s3_bucket_block)
def etl(day: Optional[datetime.datetime] = None) -> None:
    """
    Executes the Extract, Transform, Load (ETL) process for the Transformation module.

    Args:
        day (Optional[datetime.datetime], optional): The date for which the ETL process should run. If not provided, the current date is used. Defaults to None.

    Returns:
        None: This function does not return anything.

    Description:
        This function is the main entry point for the ETL process of the Transformation module. It performs the following steps:
        1. Calls the `raw_categories` task to extract raw category data.
        2. Calls the `bronze_categories` task to retrieve a list of bronze categories.
        3. Iterates over each bronze category and calls the `raw_product_category` task to extract raw product data for each category.
        4. Calls the `bronze_products` task to extract raw product data.
        5. Calls the `silver_products` task to transform the raw product data.
        6. Submits the `gold_categories` task to load the transformed category data.
        7. Submits the `gold_locations` task to load the transformed location data.
        8. Submits the `gold_products` task to load the transformed product data.

    Note:
        - The `raw_categories`, `bronze_categories`, `raw_product_category`, `bronze_products`, `silver_products`, `gold_categories`, `gold_locations`, and `gold_products` tasks are assumed to be defined in the `tasks` module.
        - The `etl` flow is decorated with the `@flow` decorator from the `prefect` library, which indicates that it is a Prefect flow.

    Example:
        ```python
        import datetime
        from orchestration.flows import etl

        # Run the ETL process for the current date
        etl()

        # Run the ETL process for a specific date
        etl(day=datetime.datetime(2022, 1, 1))
        ```
    """
    raw_categories(day=day)
    bronze_categories_list = bronze_categories()
    for category in bronze_categories_list:
        raw_product_category(
            day=day,
            category_id=category["category_id"],
            category_path_root=category["category_path_root"],
            category_search_path=category["category_search_path"],
        )

    bronze_products(day=day)
    silver_products(day=day)
    gold_categories(day=day)
    gold_locations(day=day)
    gold_products(day=day)


if __name__ == "__main__":
    etl()
