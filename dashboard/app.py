# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from wordcloud import WordCloud

st.set_page_config(layout="wide", page_title="LinkedIn Job Dashboard")

# --- Custom Top Nav ---
st.markdown(
    """
    <style>
    .main-header {
        background-color: #f5f5f5;
        padding: 1rem 2rem;
        border-bottom: 1px solid #ddd;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .main-header h2 {
        margin: 0;
        font-size: 1.8rem;
        color: #333;
    }
    .main-header a {
        margin-left: 15px;
        text-decoration: none;
        font-weight: 500;
        color: #0A66C2;
    }
    </style>
    <div class="main-header">
        <h2>Saloni Pal</h2>
        <div>
            <a href="https://www.linkedin.com/in/saloni-pal-6b58352b4" target="_blank">LinkedIn</a>
            <a href="https://github.com/Pal-Saloni" target="_blank">GitHub</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Load Data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Pal-Saloni/linkedin-job-analysis/main/cleaned/cleaned_jobs.csv"
    return pd.read_csv(url)

df = load_data()

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔽 `>> Filter Jobs`")
    location_filter = st.multiselect("🌍 Select Location(s)", options=df['LOCATION'].dropna().unique())
    job_type_filter = st.multiselect("🏠 Select Job Type(s)", options=df['ONSITE REMOTE'].dropna().unique())

# Apply filters
if location_filter:
    df = df[df['LOCATION'].isin(location_filter)]
if job_type_filter:
    df = df[df['ONSITE REMOTE'].isin(job_type_filter)]

# Title
st.markdown("## 🔍 LinkedIn Job Market Dashboard")

# --- KPIs ---
st.markdown("### 📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings", len(df))
col2.metric("Remote Jobs", df['ONSITE REMOTE'].str.contains("Remote", case=False, na=False).sum())
col3.metric("Top Hiring Location", df['LOCATION'].value_counts().idxmax())

st.divider()

# --- Top Job Titles ---
st.subheader("💼 Top Job Titles")
top_titles = df['TITLE'].value_counts().head(10)
st.bar_chart(top_titles)

# --- Top Companies ---
st.subheader("🏢 Top Hiring Companies")
top_companies = df['COMPANY'].value_counts().head(10)
st.bar_chart(top_companies)

# --- Location Chart ---
st.subheader("📍 Top Job Locations")
top_locations = df['LOCATION'].value_counts().head(10)
fig, ax = plt.subplots()
sns.barplot(x=top_locations.values, y=top_locations.index, ax=ax, palette="Blues_d")
ax.set_xlabel("Number of Jobs")
st.pyplot(fig)

# --- Remote vs Onsite ---
st.subheader("🏠 Remote vs Onsite Jobs")
remote_data = df['ONSITE REMOTE'].dropna().str.lower().value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(remote_data, labels=remote_data.index, autopct='%1.1f%%', startangle=140)
ax2.axis("equal")
st.pyplot(fig2)

# --- Date Trends ---
if 'POSTED DATE' in df.columns:
    st.subheader("📅 Job Postings Over Time")
    df['POSTED DATE'] = pd.to_datetime(df['POSTED DATE'], errors='coerce')
    time_trend = df.groupby(df['POSTED DATE'].dt.to_period('M')).size()
    st.line_chart(time_trend)

# --- Weighted Job Score ---
required_cols = {'SALARY', 'TITLE', 'COMPANY', 'DESCRIPTION', 'ONSITE REMOTE', 'LOCATION', 'CRITERIA', 'POSTED DATE', 'LINK'}
if required_cols.issubset(df.columns):
    df['job_score'] = (
        df['SALARY'].fillna(0) * 1.0 +
        df['TITLE'].fillna(0) * 0.5 +
        df['COMPANY'].fillna(0) * 0.5 +
        df['DESCRIPTION'].fillna(0) * 0.5 +
        df['ONSITE REMOTE'].fillna(0) * 0.5 +
        df['LOCATION'].fillna(0) * 0.5 +
        df['CRITERIA'].fillna(0) * 0.5 +
        df['POSTED DATE'].fillna(0) * 0.5 +
        df['LINK'].fillna(0) * 0.5
    )
    st.subheader("📈 Top Jobs by Weighted Score")
    top_jobs = df.sort_values("job_score", ascending=False).head(10)
    st.dataframe(top_jobs[['TITLE', 'COMPANY', 'LOCATION', 'job_score']])

# --- Common Criteria Analysis ---
if 'CRITERIA' in df.columns:
    st.subheader("📌 Most Common Criteria in Job Posts")
    all_criteria = ' '.join(df['CRITERIA'].dropna()).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_criteria)
    common_criteria = Counter(words).most_common(10)
    crit_df = pd.DataFrame(common_criteria, columns=['Criteria', 'Count'])
    fig_crit, ax_crit = plt.subplots()
    sns.barplot(x='Count', y='Criteria', data=crit_df, ax=ax_crit, palette='Greens_r')
    st.pyplot(fig_crit)

# --- Heatmap by Company and Location ---
if {'COMPANY', 'LOCATION'}.issubset(df.columns):
    st.subheader("🌍 Heatmap: Companies Hiring by Location")
    heatmap_data = df.groupby(['COMPANY', 'LOCATION']).size().unstack(fill_value=0)
    fig_heat, ax_heat = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax_heat)
    ax_heat.set_xlabel("Location")
    ax_heat.set_ylabel("Company")
    st.pyplot(fig_heat)

# --- Description WordCloud (Optional) ---
show_wc = st.checkbox("Show Word Cloud from Job Descriptions")
if show_wc and 'DESCRIPTION' in df.columns:
    text = ' '.join(df['DESCRIPTION'].dropna().astype(str))
    wc = WordCloud(max_words=100, background_color='white').generate(text)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wc, interpolation='bilinear')
    ax_wc.axis("off")
    st.pyplot(fig_wc)

st.markdown("---")
st.caption("Made by Saloni Pal | Data Source: LinkedIn")
