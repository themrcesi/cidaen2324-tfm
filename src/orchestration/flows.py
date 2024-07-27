import asyncio
import datetime
from typing import Optional
from prefect import flow
from .tasks import (
    raw_categories,
    bronze_categories,
    raw_product_category,
    bronze_products,
    silver_products,
)


@flow(name="etl-tfm")
async def etl(day: Optional[datetime.datetime] = None) -> None:
    raw_categories(day=day)
    bronze_categories_list = bronze_categories()
    for category in bronze_categories_list:
        raw_product_category(
            day=day,
            category_id=category["category_id"],
            category_path_root=category["category_path_root"],
            category_search_path=category["category_search_path"],
        )
    # bronze_products(day=day)
    # silver_products(day=day)


if __name__ == "__main__":
    asyncio.run(etl())
