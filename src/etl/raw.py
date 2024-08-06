import datetime
from itertools import chain
from typing import Dict, List
import requests
import asyncio
import uuid
from .utils import HEADERS, URLS, MAX_PRODUCTS


def _generate_device_id() -> str:
    generated = uuid.uuid4().__str__()
    return generated


def download_categories(day: datetime.datetime) -> Dict:
    """
    Downloads the categories from the API based on the given date.

    Parameters:
        date (datetime.datetime): The date for which the categories should be downloaded. If not provided, the current date is used.

    Returns:
        dict: A dictionary containing the downloaded categories.
    """
    response = requests.get(
        URLS["categories"], headers={**HEADERS, "X-DeviceID": _generate_device_id()}
    ).json()
    response["date"] = day.date().isoformat()
    return response


async def download_products_by_category(
    day: datetime.datetime,
    category_id: int,
    category_path_root: str,
    category_search_path: str,
    max_products: int = MAX_PRODUCTS,
) -> Dict:
    """
    Downloads the products from the API for a given category.

    Parameters:
        day (datetime.datetime): The date for which the products should be downloaded. If not provided, the current date is used.
        category_id (int): The ID of the category to download the products from.
        category_path_root (str): The root path of the category on the API.
        category_search_path (str): The search path of the category on the API.
        max_products (int): The maximum number of products to download. Defaults to MAX_PRODUCTS.

    Returns:
        dict: A dictionary containing the downloaded products.
    """

    async def _download_product_category_index(url: str, headers: Dict) -> List:
        response = await asyncio.to_thread(requests.get, url, headers=headers)
        return response.json()["search_objects"]

    try:
        returned = {"search_objects": [], "date": day.date().strftime("%Y-%m-%d")}
        results = await asyncio.gather(
            *[
                _download_product_category_index(
                    URLS["products_category"].format(
                        category_path_root=category_path_root,
                        category_search_path=category_search_path,
                        start=start,
                    ),
                    {**HEADERS, "X-DeviceID": _generate_device_id()},
                )
                for start in range(
                    0, max_products, 40
                )  # because Wallapop API only allows 40 items per request
            ]
        )
        returned["search_objects"] = list(
            map(
                lambda x: {**x, "category_id": category_id},
                chain.from_iterable(list(filter(lambda x: x != [], results))),
            )
        )
        return returned
    except Exception as e:
        print(
            f"Error downloading raw products {day} {category_path_root}-{category_search_path}: {e}"
        )
        raise
