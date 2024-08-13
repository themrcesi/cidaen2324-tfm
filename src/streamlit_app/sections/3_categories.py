import streamlit as st
from constants import S3_BUCKET_DATA, S3_BUCKET_GOLD_CATEGORIES_PATH, COLORS
import pandas as pd
import awswrangler as wr
import altair as alt

KPIS = {
    "Número de productos": "product_count",
    "Precio (media)": "price_mean",
}


@st.cache_data
def get_gold_categories() -> pd.DataFrame:
    return wr.s3.read_csv(
        path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_GOLD_CATEGORIES_PATH}"
    )


df = get_gold_categories()
pivot_area = (
    df.groupby(["date", "category_parent_display_name"])[["product_id"]]
    .sum()
    .reset_index()
    .pivot(index="date", columns="category_parent_display_name", values="product_id")
    .fillna(0)
)
pivot_area = pivot_area.reindex(
    pivot_area.sum().sort_values(ascending=False).index, axis=1
).reset_index()
subcategories_by_category = (
    df.groupby(["category_parent_display_name"])
    .count()[["category_display_name"]]
    .reset_index()
)
category_with_most_products = (
    df[df.date == df.date.max()]
    .groupby("category_parent_display_name")
    .sum(numeric_only=True)
    .nlargest(1, "product_id")
)
category_with_highest_avg_price = (
    df.groupby("category_parent_display_name")
    .mean(numeric_only=True)
    .nlargest(1, "price_mean")
)
days_creation_by_category = (
    df.groupby("category_parent_display_name")
    .agg(days_since_creation=("days_since_creation", "mean"))
    .sort_values(by="days_since_creation")
    .reset_index()
)

#############################################

st.title("Vista a nivel de Categoría!")

with st.container():
    st.markdown(
        f"En la web de Wallapop, los productos están organizados en {len(df.category_parent_display_name.unique())} categorías, que a su vez están divididas en {len(df.category_display_name.unique())} subcatgegorías."
    )
    st.bar_chart(
        subcategories_by_category,
        x="category_parent_display_name",
        y="category_display_name",
        y_label="Categoría",
        x_label="Número de subcategorías",
        horizontal=True,
        color=COLORS[0],
        stack=True,
    )

tab_general, tab_specifica = st.tabs(["Vista Agregada", "Vista Específica"])

with tab_general:
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            label="Mayor número de productos por categoría",
            value=category_with_most_products["product_id"].values[0],
            help=f"La categoría {category_with_most_products.index[0]} tiene {category_with_most_products['product_id'].values[0]} productos.",
        )
    with col2:
        st.metric(
            label="Mayor precio medio por categoría",
            value=str(round(category_with_highest_avg_price["price_mean"].values[0], 2))
            + "€",
            help=f"La categoría {category_with_highest_avg_price.index[0]} tiene {str(round(category_with_highest_avg_price['price_mean'].values[0], 2))+ '€'} de precio medio.",
        )

    with st.container():
        st.markdown(
            "A continuación se puede observar la evolución del número de productos por categoría a lo largo del tiempo."
        )
        st.area_chart(
            pivot_area,
            x="date",
            y=pivot_area.columns[1:],
            x_label="Fecha",
            y_label="Número de productos",
        )
    with st.container():
        st.markdown(
            "Además vemos la media de días que un producto lleva publicado por categoría, destacando los coches, la vivienda y los trabajos en las tres primeras posiciones (con menor número de días). Esta observación creemos que está alineada con la situación macro actual de España, indicando que estas categorías son las más demandadas."
        )
        bar_chart = (
            alt.Chart(days_creation_by_category)
            .mark_bar(color=COLORS[0])
            .encode(
                x=alt.X("category_parent_display_name:N", sort="y", title="Categoría"),
                y=alt.Y("days_since_creation:Q", title="Numero de días publicado"),
            )
        )
        st.altair_chart(bar_chart, use_container_width=True)

with tab_specifica:
    categories = df.category_parent_display_name.unique()
    with st.container():
        st.markdown(
            "*En esta vista específica, usando los filtros se puede consultar en más detalle la información disponible a nivel de categoría o subcategoría.*"
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.selectbox("Escoge una categoría", categories)
        with col2:
            subcategories = df[
                df.category_parent_display_name == category
            ].category_display_name.unique()
            subcategory = st.selectbox(
                "Escoge una subcategoría", subcategories, index=None
            )
        with col3:
            kpi = st.selectbox(
                "Escoge una métrica",
                ["Número de productos", "Precio (media)"],
                index=0,
            )

        aux = df[df.category_parent_display_name == category]
        if subcategory is not None:
            aux = aux[aux.category_display_name == subcategory]

        _df_to_plot = aux.groupby("date").agg(
            product_count=("product_id", "sum"),
            price_mean=("price_mean", "mean"),
        )
        st.line_chart(
            _df_to_plot, y=KPIS[kpi], y_label=kpi, x_label="Fecha", color=COLORS[0]
        )
