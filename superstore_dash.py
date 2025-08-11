import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore", page_icon=":bar_chart:", layout="wide")
st.title("SuperStore EDA", anchor=False)
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# File uploader
fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])

if fl is not None:
    # Read uploaded file
    df = pd.read_excel(fl)

    # Download button for uploaded dataset
    csv_uploaded = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download Uploaded Dataset",
        data=csv_uploaded,
        file_name="Uploaded_Superstore.csv",
        mime="text/csv",
        help="Click to download the uploaded Superstore dataset"
    )
    st.success(f"✅ File **{fl.name}** uploaded successfully!")
    # ------------------- Analysis Starts -------------------

    col1, col2 = st.columns((2))
    df["Order Date"] = pd.to_datetime(df["Order Date"]) 

    # Date range selection
    start_date = pd.to_datetime(df["Order Date"]).min()
    end_date = pd.to_datetime(df["Order Date"]).max()
    with col1:
        date1 = pd.to_datetime(st.date_input("Start Date", start_date))
    with col2:
        date2 = pd.to_datetime(st.date_input("End Date", end_date))

    df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()
    
    st.sidebar.header("Choose your filter: ")

    # Region filter
    region = st.sidebar.multiselect("Pick your region", df["Region"].unique())
    if not region:
        df2 = df.copy()
    else:
        df2 = df[df["Region"].isin(region)]

    # State filter
    state = st.sidebar.multiselect("Pick the State", df["State"].unique())
    if not state:
        df3 = df2.copy()
    else:
        df3 = df2[df2["State"].isin(state)]

    # City filter
    city = st.sidebar.multiselect("Pick your City", df["City"].unique())
    if not region and not state and not city:
        df4 = df
    elif not state and not city:    
        df4 = df[df["Region"].isin(region)]
    elif not region and not city:
        df4 = df3[df3["State"].isin(state)]
    elif state and city:
        df4 = df3[df["State"].isin(state) & df3["City"].isin(city)]
    elif region and city:
        df4 = df3[df["Region"].isin(state) & df3["City"].isin(city)]
    elif state and region:
        df4 = df3[df["State"].isin(state) & df3["Region"].isin(region)]
    elif city:
        df4 = df3[df3["City"].isin(city)]
    else:
        df4 = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

    # Category wise sales
    category_df = df4.groupby(by=["Category"], as_index=False)["Sales"].sum()

    with col1:
        st.subheader("Category wise Sales", anchor=False)
        fig = px.bar(category_df, x="Category", y="Sales", template='seaborn', color_discrete_sequence=["#E8E0E0"])
        st.plotly_chart(fig, use_container_width=True, height=200)
    with col2:
        st.subheader("Region wise sales", anchor=False)
        fig = px.pie(df4, values="Sales", names="Region", hole=0.5)
        fig.update_traces(text=df4["Region"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    cl1, cl2 = st.columns((2))
    with cl1:
        with st.expander("Category View Data"):
            st.write(category_df.style.background_gradient(cmap="Blues"))
            csv = category_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv", help="Click here to download the data in CSV format")
    with cl2:
        with st.expander("Region View Data"):
            region_sales = df4.groupby(by="Region", as_index=False)["Sales"].sum()
            st.write(region_sales.style.background_gradient(cmap="Blues"))
            csv = region_sales.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv", help="Click here to download the data in CSV format")

    # Time-series
    df4["month_year"] = df4["Order Date"].dt.to_period("M")
    st.subheader("Time Series Analysis", anchor=False)
    linechart = pd.DataFrame(df4.groupby(df4["month_year"].dt.strftime("%Y: %b"))["Sales"].sum()).reset_index()
    fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon", color_discrete_sequence=["#E8E0E0"])
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Time Series View Data"):
        st.write(linechart.T.style.background_gradient(cmap="Blues"))
        csv = linechart.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv", help="Click here to download the data in CSV format")

    # Tree-map
    st.header("Hierarchical view of sales using TREE MAP", anchor=False)
    fig3 = px.treemap(df4, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
    fig3.update_layout(height=700, width=800)
    st.plotly_chart(fig3, use_container_width=True)

    # Segment and Category pie charts
    chart1, chart2 = st.columns((2))
    with chart1:
        st.subheader("Segment Wise Sales", anchor=False)
        fig4 = px.pie(df4, values="Sales", names="Segment", template="plotly_dark")
        fig4.update_traces(text=df4["Segment"], textposition="inside")
        st.plotly_chart(fig4, use_container_width=True)
    with chart2:
        st.subheader("Category Wise Sales", anchor=False)
        fig4 = px.pie(df4, values="Sales", names="Category", template="plotly_dark")
        fig4.update_traces(text=df4["Category"], textposition="inside")
        st.plotly_chart(fig4, use_container_width=True)

    # Scatter-plot
    data1 = px.scatter(df4, x="Sales", y="Profit", size="Quantity")
    data1['layout'].update(
        title=dict(text="Relationship between Sales and Profit using SCATTER PLOT", font=dict(size=28)),
        xaxis=dict(title=dict(text="Sales", font=dict(size=25))),
        yaxis=dict(title=dict(text="Profit", font=dict(size=25)))
    )
    st.plotly_chart(data1, use_container_width=True)


    # with st.expander("View Data"):
    #     st.table(df)
    #     csv_filtered = df.to_csv(index=False).encode('utf-8')
    #     st.download_button(
    #         "Download Filtered Data",
    #         data=csv_filtered,
    #         file_name="Filtered_Data.csv",
    #         mime="text/csv"
    #     )

