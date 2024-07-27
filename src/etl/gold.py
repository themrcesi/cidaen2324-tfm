import datetime
import pandas as pd
from .utils import GOLD_TIMEFRAME_LIMIT, S3_BUCKET_DATA, S3_BUCKET_SILVER_PRODUCTS_PATH
from typing import List
import awswrangler as wr


def _download_products_silver(
    day: datetime.datetime, columns: List[str]
) -> pd.DataFrame:
    def _limit_gold_timeframe(
        day: datetime.datetime, n: int = GOLD_TIMEFRAME_LIMIT
    ) -> List[str]:
        end = day.date()
        return [(end - datetime.timedelta(i)).strftime("%Y-%m-%d") for i in range(n)]

    products_silver = wr.s3.read_parquet(
        f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_SILVER_PRODUCTS_PATH}",
        dataset=True,
        partition_filter=lambda x: x["date"] in _limit_gold_timeframe(day),
        columns=columns,
    )
    return products_silver


def gold_price_evolution_by_category_and_total(day: datetime.datetime) -> pd.DataFrame:
    """
    Compute the price evolution by category and the total price evolution.

    Args:
        day (datetime.datetime): The date to compute the price evolution for.

    Returns:
        pd.DataFrame: The price evolution by category and the total price evolution.
    """
    products_silver = _download_products_silver(
        day, ["date", "category_name", "category_hierarchy", "category_id", "price"]
    ).assign(
        category_display_name=lambda x: x.apply(
            lambda y: f"{y.category_name} ({y.category_hierarchy} - {y.category_id})",
            axis=1,
        )
    )
    price_evolution_by_category = (
        products_silver.groupby(["date", "category_display_name"])["price"]
        .agg(price_mean="mean", price_max="max", price_min="min")
        .reset_index()
    )
    price_evolution = (
        products_silver.groupby("date")["price"]
        .mean()
        .reset_index()
        .assign(category_display_name="All categories")
    )
    return pd.concat([price_evolution_by_category, price_evolution])


def gold_product_count_by_category_and_total(day: datetime.datetime) -> pd.DataFrame:
    """
    Compute the product count evolution by category and the total product count evolution.

    Args:
        day (datetime.datetime): The date to compute the product count evolution for.

    Returns:
        pd.DataFrame: The product count evolution by category and the total product count evolution.
    """
    products_silver = _download_products_silver(
        day,
        ["date", "category_name", "category_hierarchy", "category_id", "product_id"],
    ).assign(
        category_display_name=lambda x: x.apply(
            lambda y: f"{y.category_name} ({y.category_hierarchy} - {y.category_id})",
            axis=1,
        )
    )
    product_count_evolution_by_category = (
        products_silver.groupby(["date", "category_display_name"])["product_id"]
        .count()
        .reset_index()
    )
    product_count_evolution = (
        products_silver.groupby("date")["product_id"]
        .count()
        .reset_index()
        .assign(category_display_name="All categories")
    )
    return pd.concat([product_count_evolution_by_category, product_count_evolution])
