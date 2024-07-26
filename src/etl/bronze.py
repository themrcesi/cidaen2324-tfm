import datetime
from itertools import chain
from typing import Dict, List
import pandas as pd
from .utils import (
    S3_CLIENT,
    S3_BUCKET_DATA,
    S3_BUCKET_RAW_CATEGORY_PATH,
    S3_BUCKET_RAW_PRODUCTS_CATEGORY_PATH,
)
import json
from functools import reduce
import concurrent
import concurrent.futures
import awswrangler as wr


def _flatten_reduce_lambda(matrix):
    return list(reduce(lambda x, y: x + y, matrix, []))


def _extract_subcategories(category, category_id, path=""):
    path += " > " + category["name"] if path != "" else category["name"]
    if len(category["subcategories"]) == 0:
        return [
            {
                "category_name": category["name"],
                "category_id": category["id"],
                "category_path_root": "general",
                "category_search_path": f'category_ids={category_id}&object_type_ids={category["id"]}',
                "parent_id": category["parent_id"],
                "category_hierarchy": path,
            }
        ]
    categories = [
        _extract_subcategories(subcategory, category_id, path)
        for subcategory in category["subcategories"]
    ]
    return _flatten_reduce_lambda(categories)


def _process_category_day(json_file: str) -> List[Dict]:
    categories = []
    obj = S3_CLIENT.get_object(Bucket=S3_BUCKET_DATA, Key=json_file)
    content = obj["Body"].read().decode("utf-8")
    data = json.loads(content)
    for category in data["categories"]:
        if category["subcategories"]:
            categories.extend(_extract_subcategories(category, category["id"]))
        else:
            categories.append(
                {
                    "category_name": category["name"],
                    "category_id": category["id"],
                    "category_path_root": category["vertical_id"],
                    "category_search_path": f'category_ids={category["id"]}',
                    "parent_id": None,
                    "category_hierarchy": category["name"],
                }
            )
    return categories


def categories() -> pd.DataFrame:
    """
    Retrieves all JSON files from the S3 bucket with the given prefix and processes each file to extract category data.
    Returns a pandas DataFrame containing the processed category data, with columns for category name, category ID, category path root,
    category search path, parent ID, and category hierarchy. The DataFrame also includes additional columns for each level of the category
    hierarchy, with default values of "--" for empty levels. The DataFrame is sorted by the hierarchy length in descending order.

    Returns:
        pd.DataFrame: The processed category data.
    """
    response = S3_CLIENT.list_objects_v2(
        Bucket=S3_BUCKET_DATA, Prefix=S3_BUCKET_RAW_CATEGORY_PATH + "/"
    )
    json_files = [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".json")
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(_process_category_day, json_file)
            for json_file in json_files
        ]
        categories: List = list(
            chain.from_iterable(
                [future.result() for future in concurrent.futures.as_completed(futures)]
            )
        )
    categories_bronze = (
        pd.DataFrame(categories)
        .drop_duplicates()
        .assign(hierarchy_len=lambda x: x["category_hierarchy"].str.count(" > ") + 1)
    )
    categories_bronze = pd.concat(
        [
            categories_bronze,
            categories_bronze["category_hierarchy"]
            .str.split(
                " > ",
                expand=True,
            )
            .rename(
                columns={
                    0: "category_hierarchy_0",
                    1: "category_hierarchy_1",
                    2: "category_hierarchy_2",
                    3: "category_hierarchy_3",
                    4: "category_hierarchy_4",
                }
            ),
        ],
        axis=1,
    ).fillna(
        {
            "category_hierarchy_0": "--",
            "category_hierarchy_1": "--",
            "category_hierarchy_2": "--",
            "category_hierarchy_3": "--",
            "category_hierarchy_4": "--",
        },
    )
    return categories_bronze


def products(day: datetime.datetime) -> pd.DataFrame:
    """
    Reads JSON data from an S3 bucket and processes it to extract relevant information.
    The data is then written to a Parquet file in the S3 bucket.

    Args:
        day (datetime.datetime): The day for which the data is being processed.

    Returns:
        None
    """
    df = wr.s3.read_json(
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_RAW_PRODUCTS_CATEGORY_PATH.format(day=day.date().strftime('%Y-%m-%d'))}/"
    )
    df = df.assign(
        date=lambda x: x["date"].apply(lambda x: x.date()),
        product_id=lambda x: x["search_objects"].apply(lambda x: x["id"]),
        category_id=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["category_id"]
            if "content" in x
            else x["category_id"]
        ),
        created_at=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["creation_date"]
            if "content" in x
            else x["creation_date"]
        ),
        price=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["price"] if "content" in x else x["price"]
        ),
        currency=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["currency"] if "content" in x else x["currency"]
        ),
        title=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["title"] if "content" in x else x["title"]
        ),
        description=lambda x: x["search_objects"].apply(
            lambda x: x["content"].get("description", x["content"].get("storytelling"))
            if "content" in x
            else x.get("description", x.get("storytelling"))
        ),
        web_slug=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["web_slug"] if "content" in x else x["web_slug"]
        ),
        country_code=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["location"]["country_code"]
            if "content" in x
            else x["location"]["country_code"]
        ),
        city=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["location"]["city"]
            if "content" in x
            else x["location"]["city"]
        ),
        postal_code=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["location"]["postal_code"]
            if "content" in x
            else x["location"]["postal_code"]
        ),
        user_id=lambda x: x["search_objects"].apply(
            lambda x: x["content"]["user"]["id"] if "content" in x else x["user"]["id"]
        ),
    ).loc[
        :,
        [
            "date",
            "product_id",
            "category_id",
            "user_id",
            "created_at",
            "price",
            "currency",
            "title",
            "description",
            "web_slug",
            "country_code",
            "city",
            "postal_code",
        ],
    ]
    return df
