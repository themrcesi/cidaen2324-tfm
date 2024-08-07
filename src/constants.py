import boto3

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
ECS_PREFECT_ETL_PIPELINE_TASK_DEFINITION_ARN = (
    "arn:aws:ecs:eu-west-3:480361390441:task-definition/tfm-etl-pipeline:1"
)
