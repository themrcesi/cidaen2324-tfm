import streamlit as st

st.markdown(
    """
    Esta aplicación de Streamlit es el componente final de nuestro proyecto, diseñado para visualizar datos extraídos y transformados de la API de Wallapop. La app ofrece una interfaz sencilla que permite explorar información sobre productos, categorías y localizaciones.
    
    ## Arquitectura del Proyecto
    El proyecto sigue una arquitectura escalable y serverless, donde la ETL se orquesta mediante Prefect y se despliega en AWS. Los datos extraídos se almacenan en S3, procesándose en diferentes capas de datos (raw, bronze, silver, gold) antes de ser visualizados en la app. A continuación se muestra un diagrama que ilustra la arquitectura general del proyecto:
    """
)
st.image("imgs/arquitectura.drawio.png")
st.markdown(
    """
    ## Servicios de AWS
    El despliegue en AWS utiliza una combinación de servicios para soportar la infraestructura del proyecto. AWS Lambda maneja las tareas ligeras de la ETL, mientras que ECS con Fargate se encarga de las tareas más intensivas en memoria. S3 actúa como el datalake, almacenando los datos procesados en diferentes etapas de la pipeline. Aquí se presenta un diagrama detallado de los servicios de AWS utilizados:
    """
)
st.image("imgs/aws.drawio.png")
st.markdown(
    """
    ## Flujo de Datos
    El flujo de datos sigue una arquitectura de tipo Medallion, donde los datos pasan por múltiples etapas de procesamiento: desde la capa raw (datos crudos) hasta la capa gold (datos listos para la visualización). Prefect se encarga de orquestar todo el proceso, asegurando que cada etapa se complete correctamente antes de pasar a la siguiente. El siguiente diagrama muestra cómo fluye la información a través del sistema:
    """
)
st.image("imgs/data_flow.drawio.png")
