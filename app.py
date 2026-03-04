import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -----------------------------
# Page config with Starbucks logo
# -----------------------------
st.set_page_config(
    page_title="Starbucks EDA App",
    page_icon="starbucks_logo.png",
    layout="wide",
)

# -----------------------------
# Sidebar navigation
# -----------------------------
page = st.sidebar.selectbox(
    "Select a Page",
    ["Home", "Data Overview", "Exploratory Data Analysis"]
)

# -----------------------------
# Data loading
# -----------------------------
DATA_PATH = Path("starbucks_clean.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    return df

if not DATA_PATH.exists():
    st.error("Dataset not found. Put starbucks_clean.csv next to app.py.")
    st.stop()

df = load_data(DATA_PATH)

# -----------------------------
# Column mapping
# -----------------------------
def pick_col(options):
    for c in options:
        if c in df.columns:
            return c
    return None

COL_CAT  = pick_col(["beverage_category","Beverage_category"])
COL_BEV  = pick_col(["beverage","Beverage"])
COL_PREP = pick_col(["beverage_prep","Beverage_prep"])

COL_CAL  = pick_col(["calories","Calories"])
COL_SUG  = pick_col(["sugars_g","Sugars (g)"])
COL_CAF  = pick_col(["caffeine_mg","Caffeine (mg)"])

# -----------------------------
# App header
# -----------------------------
col1, col2 = st.columns([1,4])

with col1:
    st.image("starbucks_logo.png", width=120)

with col2:
    st.title("Starbucks Exploratory Data Analysis")

st.write("Explore Starbucks drink nutrition data with interactive filters and visualizations.")

# =============================
# HOME PAGE
# =============================
if page == "Home":

    st.header("Welcome to the Starbucks Data Explorer")

    st.image(
        "starbucks_pic_home.png",
        caption="Starbucks favorites — explore their nutrition with data ☕",
        use_container_width=True
    )

    st.markdown("### Today's goal")
    st.write(
        "Discover which Starbucks drinks are the most indulgent and which are the lighter options."
    )

    st.info("Go to the **EDA page** and use filters to explore drinks by category and preparation.")

# =============================
# DATA OVERVIEW
# =============================
elif page == "Data Overview":

    st.header("Dataset Overview")

    c1,c2,c3 = st.columns(3)

    c1.metric("Rows",df.shape[0])
    c2.metric("Columns",df.shape[1])
    c3.metric("Missing Values",int(df.isna().sum().sum()))

    st.subheader("Preview")
    st.dataframe(df.head(20),use_container_width=True)

    st.subheader("Column Types")
    st.dataframe(df.dtypes)

    st.subheader("Summary Statistics")
    st.dataframe(df.describe().T)

# =============================
# EDA PAGE
# =============================
else:

    st.header("Exploratory Data Analysis")

    st.sidebar.header("Filters")

    cat_options = ["All"] + sorted(df[COL_CAT].dropna().unique().tolist())
    selected_cat = st.sidebar.selectbox("Beverage Category",cat_options)

    filtered = df.copy()

    if selected_cat != "All":
        filtered = filtered[filtered[COL_CAT]==selected_cat]

    bev_options = ["All"] + sorted(filtered[COL_BEV].dropna().unique().tolist())
    selected_bev = st.sidebar.selectbox("Beverage",bev_options)

    if selected_bev != "All":
        filtered = filtered[filtered[COL_BEV]==selected_bev]

    prep_options = ["All"] + sorted(filtered[COL_PREP].dropna().unique().tolist())
    selected_prep = st.sidebar.selectbox("Preparation",prep_options)

    if selected_prep != "All":
        filtered = filtered[filtered[COL_PREP]==selected_prep]

    # -----------------------------
    # KPI Metrics
    # -----------------------------
    st.subheader("Key Metrics")

    k1,k2,k3,k4 = st.columns(4)

    k1.metric("Filtered Drinks",filtered.shape[0])
    k2.metric("Avg Calories",round(filtered[COL_CAL].mean(),1) if COL_CAL else "-")
    k3.metric("Avg Sugar",round(filtered[COL_SUG].mean(),1) if COL_SUG else "-")
    k4.metric("Avg Caffeine",round(filtered[COL_CAF].mean(),1) if COL_CAF else "-")

    # -----------------------------
    # Top 3 Drinks
    # -----------------------------
    st.subheader("Top 3 Highest-Calorie Drinks")

    if COL_CAL:

        top3 = filtered.sort_values(COL_CAL,ascending=False).head(3)

        for i,row in top3.iterrows():
            st.write(f"{row[COL_BEV]} — {int(row[COL_CAL])} calories")

        st.success(
            f"The most indulgent drink contains {int(top3.iloc[0][COL_CAL])} calories!"
        )

    # -----------------------------
    # Charts
    # -----------------------------
    st.subheader("Calories Distribution")

    numeric_cols = filtered.select_dtypes(include="number").columns

    hist_col = st.selectbox("Select Feature",numeric_cols)

    fig = px.histogram(filtered,x=hist_col)

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Compare Drinks")

    box_y = st.selectbox("Select Numeric Feature",numeric_cols)

    fig = px.box(filtered,x=COL_CAT,y=box_y)

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Feature Relationship")

    x_col = st.selectbox("X Axis",numeric_cols)
    y_col = st.selectbox("Y Axis",numeric_cols)

    fig = px.scatter(filtered,x=x_col,y=y_col,color=COL_CAT)

    st.plotly_chart(fig,use_container_width=True)
