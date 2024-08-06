import datetime

import pandas as pd
from .utils import (
    S3_BUCKET_DATA,
    S3_BUCKET_BRONZE_CATEGORIES_PATH,
    S3_BUCKET_BRONZE_PRODUCTS_PATH,
)
import awswrangler as wr


def products(day: datetime.datetime) -> pd.DataFrame:
    """
    Reads bronze categories and products data from S3, merges them on category_id,
    and returns a DataFrame with selected columns.

    Args:
        day (datetime.datetime): The date to filter the products data on.

    Returns:
        pd.DataFrame: The merged DataFrame.
    """
    # read categories from S3
    categories_bronze = wr.s3.read_parquet(
        f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_BRONZE_CATEGORIES_PATH}", dataset=True
    )
    # read products from S3
    products_bronze = wr.s3.read_parquet(
        f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_BRONZE_PRODUCTS_PATH}",
        dataset=True,
        partition_filter=lambda x: x["date"] == day.date().strftime("%Y-%m-%d"),
    )
    merged = (
        products_bronze.assign()
        .set_index("category_id")
        .merge(
            categories_bronze.loc[
                :, ["category_id", "category_name", "category_hierarchy"]
            ].set_index("category_id"),
            left_index=True,
            right_index=True,
            how="left",
        )
        .reset_index()
        .loc[
            :,
            [
                "product_id",
                "user_id",
                "category_id",
                "created_at",
                "title",
                "web_slug",
                "category_name",
                "category_hierarchy",
                "price",
                "currency",
                "country_code",
                "city",
                "postal_code",
                "date",
            ],
        ]
        .assign(
            days_since_creation=lambda x: x["created_at"].apply(
                lambda x: (
                    day.date()
                    - datetime.datetime.strptime(x.split("T")[0], "%Y-%m-%d").date()
                ).days
            )
        )
    )
    return merged
