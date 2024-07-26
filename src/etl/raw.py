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
    category_path_root: str,
    category_search_path: str,
    max_products: int = MAX_PRODUCTS,
) -> Dict:
    """
    Downloads products from a given category on Wallapop API.

    Args:
        day (datetime.datetime): The date of the download. Defaults to the current date if not provided.
        category_path_root (str): The ID of the category to download products from.
        category_search_path (str): The path of the category on the Wallapop API.
        recursion_limit (int, optional): The maximum number of recursive requests to make. Defaults to RECURSION_LIMIT.

    Returns:
        dict: A dictionary containing the downloaded search objects and the date of the download.

    Raises:
        None

    Example:
        >>> download_products_by_category(datetime.datetime(2022, 1, 1), 123, "path/to/category")
        {'search_objects': [...], 'date': '2022-01-01'}
    """

    async def _download_product_category_index(url: str, headers: Dict) -> List:
        response = await asyncio.to_thread(requests.get, url, headers=headers)
        return response.json()["search_objects"]

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
        chain.from_iterable(list(filter(lambda x: x != [], results)))
    )
    return returned
