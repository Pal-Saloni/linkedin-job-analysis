import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re

st.set_page_config(layout="wide", page_title="LinkedIn Job Dashboard")

# --- Inject CSS for sticky navbar and smooth scroll ---
st.markdown("""
<style>
/* Smooth Scroll */
html {
  scroll-behavior: smooth;
}

/* Sticky navbar */
.navbar {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar a {
  margin-left: 15px;
  text-decoration: none;
  font-weight: 600;
  color: #1f77b4;
}

.navbar a:hover {
  text-decoration: underline;
}

.section {
  padding-top: 60px;
  margin-top: -60px;
}
</style>
<div class="navbar">
  <div style="font-weight:bold;font-size:1.2rem;">Saloni Pal</div>
  <div>
    <a href="https://www.linkedin.com/in/saloni-pal-6b58352b4" target="_blank">LinkedIn</a>
    <a href="https://github.com/Pal-Saloni" target="_blank">GitHub</a>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Pal-Saloni/linkedin-job-analysis/main/cleaned/cleaned_jobs.csv"
    return pd.read_csv(url)

df = load_data()

# --- Sidebar Filters ---
with st.sidebar:
    st.header(">> Filter Jobs")
    location_filter = st.multiselect("📍 Select Location(s)", options=df['LOCATION'].dropna().unique())
    job_type_filter = st.multiselect("💼 Select Job Type(s)", options=df['ONSITE REMOTE'].dropna().unique())

# --- Apply Filters ---
if location_filter:
    df = df[df['LOCATION'].isin(location_filter)]
if job_type_filter:
    df = df[df['ONSITE REMOTE'].isin(job_type_filter)]

# --- Dashboard Header ---
st.title("🔍 LinkedIn Job Market Dashboard")

# --- Key Metrics ---
st.markdown('<div class="section" id="kpis"></div>', unsafe_allow_html=True)
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings", len(df))
col2.metric("Remote Jobs", df['ONSITE REMOTE'].str.contains("Remote", case=False, na=False).sum())
col3.metric("Top Hiring Location", df['LOCATION'].value_counts().idxmax())

st.divider()

# --- Top Titles ---
st.markdown('<div class="section" id="titles"></div>', unsafe_allow_html=True)
st.subheader("💼 Top Job Titles")
st.bar_chart(df['TITLE'].value_counts().head(10))

# --- Top Companies ---
st.markdown('<div class="section" id="companies"></div>', unsafe_allow_html=True)
st.subheader("🏢 Top Hiring Companies")
st.bar_chart(df['COMPANY'].value_counts().head(10))

# --- Top Locations Chart ---
st.markdown('<div class="section" id="locations"></div>', unsafe_allow_html=True)
st.subheader("📍 Top Job Locations")
fig, ax = plt.subplots()
sns.barplot(x=df['LOCATION'].value_counts().head(10).values, 
            y=df['LOCATION'].value_counts().head(10).index, palette="Blues_d", ax=ax)
ax.set_xlabel("Number of Jobs")
st.pyplot(fig)

# --- Remote vs Onsite Pie Chart ---
st.markdown('<div class="section" id="remote"></div>', unsafe_allow_html=True)
st.subheader("🏠 Remote vs Onsite Jobs")
remote_data = df['ONSITE REMOTE'].dropna().str.lower().value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(remote_data, labels=remote_data.index, autopct='%1.1f%%', startangle=140)
ax2.axis("equal")
st.pyplot(fig2)

# --- Job Postings Over Time ---
st.markdown('<div class="section" id="trends"></div>', unsafe_allow_html=True)
if 'POSTED DATE' in df.columns:
    st.subheader("📅 Job Postings Over Time")
    df['POSTED DATE'] = pd.to_datetime(df['POSTED DATE'], errors='coerce')
    trend = df.groupby(df['POSTED DATE'].dt.to_period('M')).size()
    st.line_chart(trend)

# --- Weighted Score Analysis ---
required_cols = {'SALARY', 'TITLE', 'COMPANY', 'DESCRIPTION', 'ONSITE REMOTE', 'LOCATION', 'CRITERIA', 'POSTED DATE', 'LINK'}
if required_cols.issubset(df.columns):
    st.markdown('<div class="section" id="score"></div>', unsafe_allow_html=True)
    st.subheader("📈 Top Jobs by Weighted Score")
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
    top_jobs = df.sort_values("job_score", ascending=False).head(10)
    st.dataframe(top_jobs[['TITLE', 'COMPANY', 'LOCATION', 'job_score']])

# --- Common Criteria ---
if 'CRITERIA' in df.columns:
    st.markdown('<div class="section" id="criteria"></div>', unsafe_allow_html=True)
    st.subheader("📌 Most Common Criteria in Job Posts")
    all_criteria = ' '.join(df['CRITERIA'].dropna()).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_criteria)
    common_criteria = Counter(words).most_common(10)
    crit_df = pd.DataFrame(common_criteria, columns=['Criteria', 'Count'])
    fig_c, ax_c = plt.subplots()
    sns.barplot(x='Count', y='Criteria', data=crit_df, ax=ax_c, palette='Greens_r')
    st.pyplot(fig_c)

# --- Company vs Location Heatmap ---
if {'COMPANY', 'LOCATION'}.issubset(df.columns):
    st.markdown('<div class="section" id="heatmap"></div>', unsafe_allow_html=True)
    st.subheader("🌍 Heatmap: Companies Hiring by Location")
    heatmap_data = df.groupby(['COMPANY', 'LOCATION']).size().unstack(fill_value=0)
    fig_h, ax_h = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax_h)
    ax_h.set_xlabel("Location")
    ax_h.set_ylabel("Company")
    st.pyplot(fig_h)

# --- WordCloud ---
show_wc = st.checkbox("Show Word Cloud from Descriptions")
if show_wc and 'DESCRIPTION' in df.columns:
    st.markdown('<div class="section" id="wordcloud"></div>', unsafe_allow_html=True)
    text = ' '.join(df['DESCRIPTION'].dropna().astype(str))
    wc = WordCloud(max_words=100, background_color='white').generate(text)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wc, interpolation='bilinear')
    ax_wc.axis("off")
    st.pyplot(fig_wc)

st.markdown("---")
st.caption("Made by Saloni Pal | Data Source: LinkedIn")
