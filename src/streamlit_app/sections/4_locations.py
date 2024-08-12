import streamlit as st
from constants import S3_BUCKET_DATA, S3_BUCKET_GOLD_LOCATIONS_PATH
import pandas as pd
import awswrangler as wr

KPIS = {
    "Número de productos": "product_count",
    "Precio (media)": "price_mean",
}


@st.cache_data
def get_gold_locations() -> pd.DataFrame:
    return wr.s3.read_csv(path=f"s3://{S3_BUCKET_DATA}/{S3_BUCKET_GOLD_LOCATIONS_PATH}")


df = get_gold_locations()

#############################################

st.title("Vista a nivel de Localización!")

st.markdown(
    "*Debido a las limitaciones de la API de Wallapop y para limitar el alcance de este TFM, se optó por restringir la extracción de datos a una localización concreta, el centro de Madrid. Además, la propia API no es consistente en la respuesta para los valores de localización, dejando en muchos casos este campo sin informar.*"
)

st.markdown(
    "*A raíz de estas limitaciones, esta vista se deja preparada a modo de placeholder para posibles expansiones en el futuro donde se tengan datos de varias localizaciones, permitiendo así análisis más interesantes a nivel geográfico.*"
)
