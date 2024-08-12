import streamlit as st


with st.container():
    st.image("src/streamlit_app/img/cidaen.png")
    st.markdown(
        """
        <h1 style="text-align: center;">Pipeline de Extracción y Visualización de Datos de Wallapop</h1>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(spec=[6, 4])
    with col1:
        st.subheader(
            "Autor: [César García Cabeza](https://www.linkedin.com/in/cesargarciacabeza/)"
        )
    with col2:
        st.markdown(
            """
            <h3 style="text-align: right;"><a href="https://www.cidaen.es">CIDAEN 23-24</a></h3>
            """,
            unsafe_allow_html=True,
        )
