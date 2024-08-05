import streamlit as st
from constants import S3_BUCKET_DATA, S3_BUCKET_GOLD_PRODUCTS_PATH
import pandas as pd
import awswrangler as wr

KPIS = {
    "Products Count": "product_count",
    "Price (mean)": "price_mean",
    "Price (median)": "price_median",
    "Published Days (median)": "avg_published_days",
}


@st.cache_data
def get_gold_products() -> pd.DataFrame:
    return wr.s3.read_csv(path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_GOLD_PRODUCTS_PATH}")


df = get_gold_products()
grouped = (
    df.groupby("date")
    .agg(
        product_count=("product_display_name", "count"),
        price_mean=("price", "mean"),
        price_median=("price", "median"),
        avg_published_days=("days_since_creation", "median"),
    )
    .reset_index()
)

#############################################

with st.container():
    st.title("Vista a nivel de Producto!")
    kpi = st.radio(
        "Por favor, selecciona una métrica.",
        list(KPIS.keys()),
        horizontal=True,
    )

    if kpi is not None:
        st.bar_chart(grouped, x="date", y=KPIS[kpi], x_label="Date", y_label=kpi)
