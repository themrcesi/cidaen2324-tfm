from typing import Dict
import json
import boto3


HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "es,es-ES;q=0.9",
    "Connection": "keep-alive",
    "DeviceOS": "0",
    "Host": "api.wallapop.com",
    "MPID": "-4908807427838256814",
    "Origin": "https://es.wallapop.com",
    "Referer": "https://es.wallapop.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "X-AppVersion": "81580",
    "X-DeviceOS": "0",
    "sec-ch-ua": '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

URLS = {
    "categories": "https://api.wallapop.com/api/v3/categories",
    "users": "https://api.wallapop.com/api/v3/users/{user_id}",
    "user_reviews": "https://api.wallapop.com/api/v3/users/{user_id}/reviews?init=0",
    "user_items": "https://api.wallapop.com/api/v3/users/{user_id}/items",
    "item": "https://api.wallapop.com/api/v3/items/{item_id}?language=es",
    "search": "https://api.wallapop.com/api/v3/general/search",
    "products_category": "https://api.wallapop.com/api/v3/{category_path_root}/search?{category_search_path}&latitude=40.41956&longitude=-3.69196&start={start}",
}

MAX_PRODUCTS = 10000
GOLD_TIMEFRAME_LIMIT = 30

S3_BUCKET_DATA = "cgarcia.cidaen.tfm.datalake"
S3_BUCKET_RAW_CATEGORY_PATH = "raw/categories"
S3_BUCKET_RAW_PRODUCTS_CATEGORY_PATH = "raw/products_category/{day}"
S3_BUCKET_BRONZE_CATEGORIES_PATH = "bronze/categories"
S3_BUCKET_BRONZE_PRODUCTS_PATH = "bronze/products"
S3_BUCKET_SILVER_PRODUCTS_PATH = "silver/products"
S3_BUCKET_GOLD_CATEGORIES_PATH = "gold/categories.csv"
S3_BUCKET_GOLD_LOCATIONS_PATH = "gold/locations.csv"
S3_BUCKET_GOLD_PRODUCTS_PATH = "gold/products.csv"
S3_CLIENT = boto3.client("s3")


def save_json_to_s3(bucket_name: str, key: str, json_data: Dict):
    S3_CLIENT.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(json_data),
        ContentType="application/json",
    )
