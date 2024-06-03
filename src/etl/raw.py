import datetime
from typing import Dict
import requests
from .utils import HEADERS, URLS, RECURSION_LIMIT


def download_categories(day: datetime.datetime) -> Dict:
    """
    Downloads the categories from the API based on the given date.

    Parameters:
        date (datetime.datetime): The date for which the categories should be downloaded. If not provided, the current date is used.

    Returns:
        dict: A dictionary containing the downloaded categories.
    """
    response = requests.get(URLS["categories"], headers=HEADERS).json()
    response["date"] = str(day)
    return response


def download_products_by_category(
    day: datetime.datetime,
    category_id: int,
    category_path: str,
    recursion_limit: int = RECURSION_LIMIT,
) -> Dict:
    """
    Downloads products from a given category on Wallapop API.

    Args:
        day (datetime.datetime): The date of the download. Defaults to the current date if not provided.
        category_id (int): The ID of the category to download products from.
        category_path (str): The path of the category on the Wallapop API.
        recursion_limit (int, optional): The maximum number of recursive requests to make. Defaults to RECURSION_LIMIT.

    Returns:
        dict: A dictionary containing the downloaded search objects and the date of the download.

    Raises:
        None

    Example:
        >>> download_products_by_category(datetime.datetime(2022, 1, 1), 123, "path/to/category")
        {'search_objects': [...], 'date': '2022-01-01'}
    """
    recursive_requests = 1
    returned = {"search_objects": [], "date": str(day)}
    start = 0
    while True:
        if recursive_requests < recursion_limit:
            url = f"https://api.wallapop.com/api/v3/{category_path}/search?category_ids={category_id}&latitude=40.41956&longitude=-3.69196&start={start}"
            result = requests.get(url, headers=HEADERS).json()
            search_objects = result["search_objects"]
            if len(search_objects) == 0:
                break
            start += len(search_objects)
            returned["search_objects"].extend(search_objects)
            recursive_requests += 1
        else:
            break
    return returned
