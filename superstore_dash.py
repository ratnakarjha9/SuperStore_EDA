import streamlit as st
import plotly.express as px
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 SuperStore EDA Dashboard")
st.markdown("---")

# ===========================
# Download Sample Dataset
# ===========================

st.subheader("Download Sample Dataset")

try:
    with open("Superstore.xlsx", "rb") as file:
        st.download_button(
            label="📥 Download Sample Superstore Dataset",
            data=file,
            file_name="Superstore.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
except FileNotFoundError:
    st.warning("Sample dataset (Superstore.xlsx) not found in the project folder.")

st.info("If you already have the dataset, simply upload it below.")

# ===========================
# Upload Dataset
# ===========================

fl = st.file_uploader(
    "📂 Upload Superstore Dataset",
    type=["csv", "xlsx", "xls"]
)

if fl is not None:

    # Read file
    try:
        if fl.name.endswith(".csv"):
            df = pd.read_csv(fl)
        else:
            df = pd.read_excel(fl)
    except Exception as e:
        st.error(f"Error reading file:\n{e}")
        st.stop()

    # Required Columns
    required_columns = [
        "Order Date",
        "Region",
        "State",
        "City",
        "Category",
        "Sub-Category",
        "Segment",
        "Sales",
        "Profit",
        "Quantity",
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        st.error(f"Missing Columns: {missing}")
        st.stop()

    st.success(f"✅ {fl.name} uploaded successfully!")

    # Download Uploaded Dataset
    csv_uploaded = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Uploaded Dataset",
        csv_uploaded,
        "Uploaded_Superstore.csv",
        "text/csv",
    )

    # ===========================
    # Data Cleaning
    # ===========================

    df["Order Date"] = pd.to_datetime(df["Order Date"])

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            df["Order Date"].min()
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            df["Order Date"].max()
        )

    df = df[
        (df["Order Date"] >= pd.to_datetime(start_date))
        & (df["Order Date"] <= pd.to_datetime(end_date))
    ]

    # ===========================
    # Sidebar Filters
    # ===========================

    st.sidebar.header("Choose Filters")

    region = st.sidebar.multiselect(
        "Region",
        sorted(df["Region"].unique())
    )

    state = st.sidebar.multiselect(
        "State",
        sorted(df["State"].unique())
    )

    city = st.sidebar.multiselect(
        "City",
        sorted(df["City"].unique())
    )

    df4 = df.copy()

    if region:
        df4 = df4[df4["Region"].isin(region)]

    if state:
        df4 = df4[df4["State"].isin(state)]

    if city:
        df4 = df4[df4["City"].isin(city)]

    # ===========================
    # Category Sales
    # ===========================

    category_df = (
        df4.groupby("Category", as_index=False)["Sales"]
        .sum()
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Category Wise Sales")

        fig = px.bar(
            category_df,
            x="Category",
            y="Sales",
            template="plotly_white",
            color="Category"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        st.subheader("Region Wise Sales")

        fig = px.pie(
            df4,
            values="Sales",
            names="Region",
            hole=0.5
        )

        fig.update_traces(textinfo="percent+label")

        st.plotly_chart(fig, use_container_width=True)

    # ===========================
    # Download Tables
    # ===========================

    c1, c2 = st.columns(2)

    with c1:

        with st.expander("Category Data"):

            st.dataframe(category_df)

            st.download_button(
                "Download Category Data",
                category_df.to_csv(index=False),
                "Category.csv",
                "text/csv",
            )

    with c2:

        with st.expander("Region Data"):

            region_df = (
                df4.groupby("Region", as_index=False)["Sales"]
                .sum()
            )

            st.dataframe(region_df)

            st.download_button(
                "Download Region Data",
                region_df.to_csv(index=False),
                "Region.csv",
                "text/csv",
            )

    # ===========================
    # Time Series
    # ===========================

    df4 = df4.copy()

    df4["Month"] = df4["Order Date"].dt.to_period("M")

    linechart = (
        df4.groupby("Month")["Sales"]
        .sum()
        .reset_index()
    )

    linechart["Month"] = linechart["Month"].astype(str)

    st.subheader("Time Series Analysis")

    fig = px.line(
        linechart,
        x="Month",
        y="Sales",
        template="plotly_white",
        markers=True,
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Time Series Data"):

        st.dataframe(linechart)

        st.download_button(
            "Download Time Series",
            linechart.to_csv(index=False),
            "TimeSeries.csv",
            "text/csv",
        )

    # ===========================
    # Treemap
    # ===========================

    st.header("Hierarchical Sales View")

    fig = px.treemap(
        df4,
        path=["Region", "Category", "Sub-Category"],
        values="Sales",
        color="Category"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ===========================
    # Pie Charts
    # ===========================

    c1, c2 = st.columns(2)

    with c1:

        st.subheader("Segment Wise Sales")

        fig = px.pie(
            df4,
            values="Sales",
            names="Segment"
        )

        fig.update_traces(textinfo="percent+label")

        st.plotly_chart(fig, use_container_width=True)

    with c2:

        st.subheader("Category Wise Sales")

        fig = px.pie(
            df4,
            values="Sales",
            names="Category"
        )

        fig.update_traces(textinfo="percent+label")

        st.plotly_chart(fig, use_container_width=True)

    # ===========================
    # Scatter Plot
    # ===========================

    st.subheader("Sales vs Profit")

    fig = px.scatter(
        df4,
        x="Sales",
        y="Profit",
        size="Quantity",
        color="Category",
        hover_name="Sub-Category",
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("⬆ Please upload a dataset to begin analysis.")
