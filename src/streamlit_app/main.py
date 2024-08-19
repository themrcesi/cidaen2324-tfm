import streamlit as st

pg = st.navigation(
    [
        st.Page("sections/0_portada.py", title="Home", icon=":material/home:"),
        st.Page(
            "sections/1_intro.py", title="Introducción", icon=":material/overview:"
        ),
        st.Page(
            "sections/2_products.py", title="Productos", icon=":material/inventory:"
        ),
        st.Page(
            "sections/3_categories.py", title="Categorías", icon=":material/category:"
        ),
        st.Page(
            "sections/4_locations.py", title="Localizaciones", icon=":material/explore:"
        ),
    ]
)
pg.run()
