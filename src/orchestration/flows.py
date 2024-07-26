import asyncio
from prefect import flow
from .tasks import raw_categories, bronze_categories, raw_product_category


@flow(name="etl-tfm")
async def etl() -> None:
    import time

    raw_categories()
    bronze_categories_list = bronze_categories()
    start = time.time()
    for category in bronze_categories_list:
        raw_product_category(
            category_id=category["category_id"],
            category_path_root=category["category_path_root"],
            category_search_path=category["category_search_path"],
        )
    print("time", time.time() - start)


if __name__ == "__main__":
    asyncio.run(etl())
