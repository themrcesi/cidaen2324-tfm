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
        returned = [
            (end - datetime.timedelta(i)).strftime("%Y-%m-%d") for i in range(n)
        ]
        return returned

    products_silver = wr.s3.read_parquet(
        f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_SILVER_PRODUCTS_PATH}/",
        dataset=True,
        partition_filter=lambda x: (x["date"] in _limit_gold_timeframe(day)),
        columns=columns,
    )
    return products_silver


def gold_category_and_total(day: datetime.datetime) -> pd.DataFrame:
    """
    Generate a DataFrame with the price and count evolution of categories over time.

    Parameters:
        day (datetime.datetime): The date for which to calculate the category evolution.

    Returns:
        pd.DataFrame: A DataFrame with the following columns:
            - date (datetime.datetime): The date.
            - category_display_name (str): The display name of the category.
            - price_mean (float): The mean price of the category.
            - price_max (float): The maximum price of the category.
            - price_min (float): The minimum price of the category.
            - count (int): The number of products in the category.
            - category_parent_display_name (str): The display name of the parent category.

    The DataFrame also includes a row for the '--' category.
    """
    products_silver = _download_products_silver(
        day,
        [
            "date",
            "category_name",
            "category_hierarchy",
            "category_id",
            "price",
            "product_id",
            "days_since_creation",
        ],
    ).assign(
        category_display_name=lambda x: x.apply(
            lambda y: f"{y.category_name} ({y.category_hierarchy} - {y.category_id})",
            axis=1,
        )
    )
    price_evolution = pd.concat(
        [
            (
                products_silver.groupby(
                    [
                        "date",
                        "category_display_name",
                    ],
                    observed=True,
                )["price"]
                .agg(price_mean="mean", price_max="max", price_min="min")
                .reset_index()
            ),
            (
                products_silver.groupby("date", observed=True)["price"]
                .agg(price_mean="mean", price_max="max", price_min="min")
                .reset_index()
                .assign(category_display_name="--")
            ),
        ]
    )
    count_evolution = pd.concat(
        [
            (
                products_silver.groupby(
                    [
                        "date",
                        "category_display_name",
                    ],
                    observed=True,
                )["product_id"]
                .count()
                .reset_index()
            ),
            (
                products_silver.groupby("date", observed=True)["product_id"]
                .count()
                .reset_index()
                .assign(category_display_name="--")
            ),
        ]
    )
    item_duration_evolution = pd.concat(
        [
            (
                products_silver.groupby(
                    [
                        "date",
                        "category_display_name",
                    ],
                    observed=True,
                )["days_since_creation"]
                .mean()
                .reset_index()
            ),
            (
                products_silver.groupby("date", observed=True)["days_since_creation"]
                .mean()
                .reset_index()
                .assign(category_display_name="--")
            ),
        ]
    )
    return (
        price_evolution.merge(
            count_evolution,
            on=["date", "category_display_name"],
        )
        .merge(
            item_duration_evolution,
            on=["date", "category_display_name"],
        )
        .merge(
            products_silver.assign(
                category_parent_display_name=lambda x: x.category_hierarchy.apply(
                    lambda y: y.split(" > ")[0]
                )
            )[
                ["category_display_name", "category_parent_display_name"]
            ].drop_duplicates(),
            on="category_display_name",
        )
    )


def gold_location_and_total(day: datetime.datetime) -> pd.DataFrame:
    """
    Retrieves the gold data for location and total data for a given day.

    Args:
        day (datetime.datetime): The date for which to retrieve the data.

    Returns:
        pd.DataFrame: A DataFrame containing the gold location and total data. The DataFrame has the following columns:
            - date (datetime.datetime): The date.
            - location_display_name (str): The display name of the location.
            - postal_code (str): The postal code of the location.
            - city_display_name (str): The display name of the city.
            - price_mean (float): The mean price of the location.
            - price_max (float): The maximum price of the location.
            - price_min (float): The minimum price of the location.
            - product_id (int): The number of products in the location.
            - days_since_creation (float): The mean number of days since creation of the products in the location.

    The DataFrame also includes a row for the '--' location.
    """
    products_silver = _download_products_silver(
        day,
        [
            "date",
            "country_code",
            "city",
            "postal_code",
            "price",
            "product_id",
            "days_since_creation",
        ],
    ).assign(
        location_display_name=lambda x: x.apply(
            lambda y: f"{y.city}, {y.country_code} ({y.postal_code})",
            axis=1,
        ),
        city_display_name=lambda x: x.apply(
            lambda y: f"{y.city}, {y.country_code}",
            axis=1,
        ),
    )
    price_evolution = pd.concat(
        [
            (
                products_silver.groupby(
                    [
                        "date",
                        "city_display_name",
                        "postal_code",
                        "location_display_name",
                    ],
                    observed=True,
                )["price"]
                .agg(price_mean="mean", price_max="max", price_min="min")
                .reset_index()
            ),
            (
                products_silver.groupby("date", observed=True)["price"]
                .agg(price_mean="mean", price_max="max", price_min="min")
                .reset_index()
                .assign(
                    location_display_name="--", postal_code="--", city_display_name="--"
                )
            ),
        ]
    )
    count_evolution = pd.concat(
        [
            (
                products_silver.groupby(
                    [
                        "date",
                        "city_display_name",
                        "postal_code",
                        "location_display_name",
                    ],
                    observed=True,
                )["product_id"]
                .count()
                .reset_index()
            ),
            (
                products_silver.groupby("date", observed=True)["product_id"]
                .count()
                .reset_index()
                .assign(
                    location_display_name="--", postal_code="--", city_display_name="--"
                )
            ),
        ]
    )
    item_duration_evolution = pd.concat(
        [
            (
                products_silver.groupby(
                    [
                        "date",
                        "city_display_name",
                        "postal_code",
                        "location_display_name",
                    ],
                    observed=True,
                )["days_since_creation"]
                .mean()
                .reset_index()
            ),
            (
                products_silver.groupby("date", observed=True)["days_since_creation"]
                .mean()
                .reset_index()
                .assign(
                    location_display_name="--", postal_code="--", city_display_name="--"
                )
            ),
        ]
    )
    return price_evolution.merge(
        count_evolution,
        on=["date", "location_display_name", "city_display_name", "postal_code"],
    ).merge(
        item_duration_evolution,
        on=["date", "location_display_name", "city_display_name", "postal_code"],
    )


def gold_product(day: datetime.datetime) -> pd.DataFrame:
    """
    Retrieves the product information for a specific day from the `products_silver` DataFrame.

    Args:
        day (datetime.datetime): The date for which the product information is requested.

    Returns:
        pd.DataFrame: A DataFrame containing the following columns:
            - date (datetime): The date of the product.
            - product_display_name (str): The product name and ID.
            - web_slug (str): The web URL slug of the product.
            - price (float): The price of the product.
            - days_since_creation (int): The number of days since the product was created.
    """
    products_silver = _download_products_silver(
        day,
        [
            "date",
            "title",
            "web_slug",
            "price",
            "product_id",
            "days_since_creation",
        ],
    ).assign(
        product_display_name=lambda x: x.apply(
            lambda y: f"{y.title} ({y.product_id})",
            axis=1,
        )
    )
    returned = products_silver[
        ["date", "product_display_name", "web_slug", "price", "days_since_creation"]
    ]
    return returned
