from etl.bronze import products
import awswrangler as wr
from etl.utils import S3_BUCKET_DATA, S3_BUCKET_BRONZE_PRODUCTS_PATH
import os
import datetime

if __name__ == "__main__":
    day = (
        datetime.datetime.fromisoformat(inputt)
        if (inputt := os.getenv("day"))
        else datetime.datetime.today()
    )
    bronze_products_df = products(day)
    wr.s3.to_parquet(
        df=bronze_products_df,
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_BRONZE_PRODUCTS_PATH}",
        dataset=True,
        partition_cols=["date"],
        mode="overwrite_partitions",
    )
