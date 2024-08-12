import streamlit as st
from constants import S3_BUCKET_DATA, S3_BUCKET_GOLD_PRODUCTS_PATH
import pandas as pd
import awswrangler as wr
from constants import COLORS
import datetime

KPIS = {
    "Número de productos": "product_count",
    "Precio (media)": "price_mean",
    "Precio (mediana)": "price_median",
    "Días publicado (media)": "avg_published_days",
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

st.title("Vista a nivel de Producto!")

st.markdown(
    f"En total hay {len(df.product_display_name.unique())} productos descargados, con datos para {len(df.date.unique())} días. En esta vista se puede consultar una serie de información básica a nivel de producto, bien agregado o específico."
)

tab_general, tab_especifica = st.tabs(["General", "Específica"])
with tab_general:
    with st.container():
        kpi = st.radio(
            "Por favor, selecciona una métrica para ver su evolución agregada a nivel de producto.",
            list(KPIS.keys()),
            horizontal=True,
        )

        if kpi is not None:
            st.bar_chart(
                grouped,
                x="date",
                y=KPIS[kpi],
                x_label="Día",
                y_label=kpi,
                color=COLORS[0],
            )

with tab_especifica:
    with st.container():
        option = st.selectbox(
            "También puedes filtrar un producto en específico para ver la evolución de su precio si lo deseas.",
            set(df.product_display_name.unique()),
            index=None,
            placeholder="Escoge un producto...",
        )
        if option is not None:
            url_slug = df[df.product_display_name == option].web_slug.unique()[0]
            product_df = (
                df[df.product_display_name == option]
                .groupby("date")
                .agg(price=("price", "mean"))
                .reset_index()
            )
            _aux = df[df.product_display_name == option].iloc[0]
            creation_date = (
                datetime.datetime.fromisoformat(_aux.date)
                - datetime.timedelta(days=int(_aux.days_since_creation))
            ).strftime("%Y-%m-%d")
            st.markdown(
                f"*[{option}](https://es.wallapop.com/item/{url_slug}) | Fecha de publicación: {creation_date}*"
            )
            st.line_chart(
                product_df,
                x="date",
                y="price",
                x_label="Date",
                y_label="Price",
                color=COLORS[0],
            )
