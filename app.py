
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Scientific Visualisation",
    page_icon="📊",
    layout="wide"
)

st.title("Scientific Visualisation Dashboard")
st.write(
    "Exploring relationships between annual live births, "
    "household income, and school completion rates across Malaysian states."
)

st.success("Your Streamlit application is ready!")

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Objective",
    [
        "Objective 1: Births & Income",
        "Objective 2: Education & Income",
        "Objective 3: Births & Education"
    ]
)

if page == "Objective 1: Births & Income":
    st.header("Objective 1")
    st.write(
        "To identify the relationship between annual live births "
        "and household income across Malaysian states."
    )

elif page == "Objective 2: Education & Income":
    st.header("Objective 2")
    st.write(
        "To examine the relationship between school completion "
        "rates and household income across Malaysian states."
    )

else:
    st.header("Objective 3")
    st.write(
        "To analyze the relationship between annual live births "
        "and school completion rates across Malaysian states."
    )
