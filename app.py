import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Charter vs. Non-Charter Yield Rates", layout="wide")

st.title("Charter vs. Non-Charter School Yield Rates")
st.markdown(
    "Comparing enrollment yield rates (**enrollees / applicants**) for charter vs. "
    "non-charter schools, Fall 2023–2025."
)

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard_data.csv")
    return df

dashboard_data = load_data()
dashboard_data = dashboard_data[dashboard_data["fall_term"].isin([2023, 2024, 2025])]

# -------------------------------------------------
# ANALYSIS (cleaned-up version of your original code)
# Instead of repeating the same filter/sum logic 3 times per year,
# groupby does it for every year x charter status at once.
# -------------------------------------------------
yield_summary = (
    dashboard_data
    .groupby(["fall_term", "charter"])
    .agg(applicants=("applicants", "sum"), enrollees=("enrollees", "sum"))
    .reset_index()
)
yield_summary["yield_rate"] = yield_summary["enrollees"] / yield_summary["applicants"]

# Pivot so each row = a year, columns = charter (Y) vs non-charter (N)
pivot = yield_summary.pivot(index="fall_term", columns="charter", values="yield_rate")
pivot = pivot.rename(columns={"Y": "Charter", "N": "Non-Charter"})

# -------------------------------------------------
# SIDEBAR FILTERS (optional interactivity)
# -------------------------------------------------
st.sidebar.header("Filters")
years_available = sorted(dashboard_data["fall_term"].unique())
selected_years = st.sidebar.multiselect(
    "Select years to include", years_available, default=years_available
)

filtered_pivot = pivot.loc[pivot.index.isin(selected_years)]

# -------------------------------------------------
# METRICS ROW (quick-glance numbers)
# -------------------------------------------------
col1, col2 = st.columns(2)
latest_year = max(selected_years) if selected_years else years_available[-1]
col1.metric(
    f"Charter Yield Rate ({latest_year})",
    f"{filtered_pivot.loc[latest_year, 'Charter']:.1%}"
)
col2.metric(
    f"Non-Charter Yield Rate ({latest_year})",
    f"{filtered_pivot.loc[latest_year, 'Non-Charter']:.1%}"
)

# -------------------------------------------------
# CHART 1: Line chart — trend over time
# -------------------------------------------------
st.subheader("Yield Rate Trend Over Time")
st.line_chart(filtered_pivot)

# -------------------------------------------------
# CHART 2: Bar chart — side-by-side comparison per year
# -------------------------------------------------
st.subheader("Yield Rate by Year (Bar Comparison)")
fig, ax = plt.subplots(figsize=(8, 4))
filtered_pivot.plot(kind="bar", ax=ax)
ax.set_ylabel("Yield Rate")
ax.set_xlabel("Fall Term")
ax.set_title("Charter vs. Non-Charter Yield Rate")
ax.legend(title="School Type")
st.pyplot(fig)

# -------------------------------------------------
# RAW DATA TABLE (nice to show for transparency / judges)
# -------------------------------------------------
with st.expander("See underlying data"):
    st.dataframe(filtered_pivot.style.format("{:.1%}"))
