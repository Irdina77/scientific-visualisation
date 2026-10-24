
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Scientific Visualisation",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    births = pd.read_csv("birth_state.csv")
    income = pd.read_csv("hh_income_state.csv")
    school = pd.read_csv("completion_school_state.csv")

    for df in [births, income, school]:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = df["date"].dt.year

    births = births.rename(columns={"abs": "live_births"})
    return births, income, school

births, income, school = load_data()

st.title("Scientific Visualisation Dashboard")
st.caption(
    "Exploring relationships between live births, "
    "household income and school completion in Malaysia"
)

page = st.sidebar.radio(
    "Select Objective",
    [
        "Objective 1: Births & Income",
        "Objective 2: Education & Income",
        "Objective 3: Births & Education"
    ]
)

states = sorted(set(births["state"].dropna()) &
                set(income["state"].dropna()) &
                set(school.loc[school["state"] != "Malaysia",
                              "state"].dropna()))

selected_state = st.sidebar.selectbox(
    "Select State",
    ["All States"] + states
)

def filter_state(df):
    if selected_state != "All States":
        return df[df["state"] == selected_state].copy()
    return df.copy()

def summary(label, value, help_text=None):
    st.metric(label, value, help=help_text)

def scatter_chart(df, x, y, title, x_label, y_label):
    data = df.dropna(subset=[x, y]).copy()
    if data.empty:
        st.info("No matching data available for this chart.")
        return
    fig = px.scatter(
        data, x=x, y=y, color="state",
        hover_data=["year"],
        trendline="ols" if len(data) >= 3 else None,
        title=title,
        labels={x: x_label, y: y_label}
    )
    st.plotly_chart(fig, use_container_width=True)

def correlation_chart(df, x, y, title):
    data = df[[x, y]].dropna()
    if len(data) < 2:
        st.info("Not enough overlapping data to calculate correlation.")
        return
    corr = data.corr().iloc[0, 1]
    st.metric("Pearson correlation", f"{corr:.3f}")
    st.caption(
        "Correlation describes association, not causation. "
        "A value near +1 is positive, near -1 is negative, "
        "and near 0 indicates little linear association."
    )
    fig = px.imshow(
        data.corr(),
        text_auto=".2f",
        zmin=-1, zmax=1,
        color_continuous_scale="RdBu",
        title=title
    )
    st.plotly_chart(fig, use_container_width=True)

if page == "Objective 1: Births & Income":
    st.header("Objective 1: Live Births and Household Income")
    st.write(
        "To identify the relationship between annual live births "
        "and household income across Malaysian states."
    )

    b = filter_state(births)
    i = filter_state(income)
    merged = b.merge(i, on=["state", "year"], how="inner")
    merged = merged.dropna(subset=["live_births", "income_mean"])

    if not merged.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total live births", f"{merged['live_births'].sum():,.0f}")
        c2.metric("Average household income",
                  f"{merged['income_mean'].mean():,.0f}")
        corr = merged["live_births"].corr(merged["income_mean"])
        c3.metric("Correlation", f"{corr:.3f}" if pd.notna(corr) else "N/A")

        st.subheader("Visualization 1: Scatter Plot")
        scatter_chart(
            merged, "income_mean", "live_births",
            "Household Income vs Live Births",
            "Mean Household Income", "Number of Live Births"
        )

        st.subheader("Visualization 2: State Comparison")
        latest_year = int(merged["year"].max())
        latest = merged[merged["year"] == latest_year]
        fig = px.bar(
            latest, x="state", y="live_births",
            color="income_mean",
            title=f"Live Births by State ({latest_year})",
            labels={"state": "State", "live_births": "Live Births",
                    "income_mean": "Mean Household Income"}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Visualization 3: Correlation")
        correlation_chart(
            merged, "income_mean", "live_births",
            "Correlation Between Income and Live Births"
        )
    else:
        st.warning("No matching state and year records were found.")

elif page == "Objective 2: Education & Income":
    st.header("Objective 2: School Completion and Household Income")
    st.write(
        "To examine the relationship between school completion "
        "rates and household income across Malaysian states."
    )

    s = filter_state(school)
    i = filter_state(income)
    s = s[s["sex"].str.lower() == "both"]
    merged = s.merge(i, on=["state", "year"], how="inner")
    merged = merged.dropna(subset=["completion", "income_mean"])

    if not merged.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Mean completion rate",
                  f"{merged['completion'].mean():.2f}%")
        c2.metric("Average household income",
                  f"{merged['income_mean'].mean():,.0f}")
        corr = merged["completion"].corr(merged["income_mean"])
        c3.metric("Correlation", f"{corr:.3f}" if pd.notna(corr) else "N/A")

        st.subheader("Visualization 1: Scatter Plot")
        scatter_chart(
            merged, "income_mean", "completion",
            "Household Income vs School Completion",
            "Mean Household Income", "Completion Rate (%)"
        )

        st.subheader("Visualization 2: Education Stage Comparison")
        latest_year = int(merged["year"].max())
        latest = merged[merged["year"] == latest_year]
        fig = px.bar(
            latest, x="state", y="completion", color="stage",
            barmode="group",
            title=f"Completion Rate by State and Stage ({latest_year})",
            labels={"state": "State", "completion": "Completion Rate (%)",
                    "stage": "Education Stage"}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Visualization 3: Correlation")
        correlation_chart(
            merged, "income_mean", "completion",
            "Correlation Between Income and School Completion"
        )
    else:
        st.warning("No matching state and year records were found.")

else:
    st.header("Objective 3: Live Births and School Completion")
    st.write(
        "To analyze the relationship between annual live births "
        "and school completion rates across Malaysian states."
    )

    b = filter_state(births)
    s = filter_state(school)
    s = s[s["sex"].str.lower() == "both"]
    merged = b.merge(s, on=["state", "year"], how="inner")
    merged = merged.dropna(subset=["live_births", "completion"])

    if not merged.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total live births", f"{merged['live_births'].sum():,.0f}")
        c2.metric("Mean completion rate",
                  f"{merged['completion'].mean():.2f}%")
        corr = merged["live_births"].corr(merged["completion"])
        c3.metric("Correlation", f"{corr:.3f}" if pd.notna(corr) else "N/A")

        st.subheader("Visualization 1: Scatter Plot")
        scatter_chart(
            merged, "live_births", "completion",
            "Live Births vs School Completion",
            "Number of Live Births", "Completion Rate (%)"
        )

        st.subheader("Visualization 2: State Comparison")
        latest_year = int(merged["year"].max())
        latest = merged[merged["year"] == latest_year]
        fig = px.scatter(
            latest, x="live_births", y="completion",
            color="state", size="live_births",
            hover_name="state",
            title=f"State Comparison ({latest_year})",
            labels={"live_births": "Live Births",
                    "completion": "Completion Rate (%)"}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Visualization 3: Correlation")
        correlation_chart(
            merged, "live_births", "completion",
            "Correlation Between Live Births and School Completion"
        )
    else:
        st.warning("No matching state and year records were found.")

st.divider()
st.caption(
    "Note: Analyses use matching state-year records. "
    "Results depend on the years available in each dataset."
)
