import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re

st.set_page_config(layout="wide", page_title="LinkedIn Job Dashboard")

# --- Inject CSS & Sticky Navbar with Smooth Scroll ---
st.markdown("""
<style>
html {
  scroll-behavior: smooth;
}

.navbar {
  position: fixed;
  top: 0;
  width: 100%;
  background-color: white;
  border-bottom: 1px solid #ddd;
  z-index: 999;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
}

.navbar-left {
  font-size: 1.4rem;
  font-weight: bold;
}

.navbar-right a {
  margin-left: 20px;
  text-decoration: none;
  font-weight: 600;
  color: #1f77b4;
}

.navbar-right a:hover {
  text-decoration: underline;
}

.section {
  padding-top: 80px;
  margin-top: -80px;
}
</style>

<div class="navbar">
  <div class="navbar-left">Saloni Pal</div>
  <div class="navbar-right">
    <a href="#kpis">📊 Metrics</a>
    <a href="#titles">💼 Titles</a>
    <a href="#companies">🏢 Companies</a>
    <a href="#locations">📍 Locations</a>
    <a href="#remote">🏠 Remote/Onsite</a>
    <a href="#trends">📅 Trends</a>
    <a href="#score">📈 Scores</a>
    <a href="#criteria">📌 Criteria</a>
    <a href="#heatmap">🌍 Heatmap</a>
    <a href="#wordcloud">☁ WordCloud</a>
    <a href="https://www.linkedin.com/in/saloni-pal-6b58352b4" target="_blank">LinkedIn</a>
    <a href="https://github.com/Pal-Saloni" target="_blank">GitHub</a>
  </div>
</div>

<br><br><br>
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

if location_filter:
    df = df[df['LOCATION'].isin(location_filter)]
if job_type_filter:
    df = df[df['ONSITE REMOTE'].isin(job_type_filter)]

st.title("🔍 LinkedIn Job Market Dashboard")

# --- Section: KPIs ---
st.markdown('<div class="section" id="kpis"></div>', unsafe_allow_html=True)
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings", len(df))
col2.metric("Remote Jobs", df['ONSITE REMOTE'].str.contains("Remote", case=False, na=False).sum())
col3.metric("Top Hiring Location", df['LOCATION'].value_counts().idxmax())
st.divider()

# --- Section: Top Titles ---
st.markdown('<div class="section" id="titles"></div>', unsafe_allow_html=True)
st.subheader("💼 Top Job Titles")
st.bar_chart(df['TITLE'].value_counts().head(10))

# --- Section: Top Companies ---
st.markdown('<div class="section" id="companies"></div>', unsafe_allow_html=True)
st.subheader("🏢 Top Hiring Companies")
st.bar_chart(df['COMPANY'].value_counts().head(10))

# --- Section: Locations ---
st.markdown('<div class="section" id="locations"></div>', unsafe_allow_html=True)
st.subheader("📍 Top Job Locations")
fig, ax = plt.subplots()
sns.barplot(x=df['LOCATION'].value_counts().head(10).values, 
            y=df['LOCATION'].value_counts().head(10).index, palette="Blues_d", ax=ax)
ax.set_xlabel("Number of Jobs")
st.pyplot(fig)

# --- Section: Remote vs Onsite ---
st.markdown('<div class="section" id="remote"></div>', unsafe_allow_html=True)
st.subheader("🏠 Remote vs Onsite Jobs")
remote_data = df['ONSITE REMOTE'].dropna().str.lower().value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(remote_data, labels=remote_data.index, autopct='%1.1f%%', startangle=140)
ax2.axis("equal")
st.pyplot(fig2)

# --- Section: Trends ---
st.markdown('<div class="section" id="trends"></div>', unsafe_allow_html=True)
if 'POSTED DATE' in df.columns:
    st.subheader("📅 Job Postings Over Time")
    df['POSTED DATE'] = pd.to_datetime(df['POSTED DATE'], errors='coerce')
    trend = df.groupby(df['POSTED DATE'].dt.to_period('M')).size()
    st.line_chart(trend)

# --- Section: Weighted Score ---
st.markdown('<div class="section" id="score"></div>', unsafe_allow_html=True)
if {'SALARY', 'TITLE', 'COMPANY', 'DESCRIPTION', 'ONSITE REMOTE', 'LOCATION', 'CRITERIA', 'POSTED DATE', 'LINK'}.issubset(df.columns):
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

# --- Section: Criteria ---
st.markdown('<div class="section" id="criteria"></div>', unsafe_allow_html=True)
if 'CRITERIA' in df.columns:
    st.subheader("📌 Most Common Criteria in Job Posts")
    all_criteria = ' '.join(df['CRITERIA'].dropna()).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_criteria)
    common_criteria = Counter(words).most_common(10)
    crit_df = pd.DataFrame(common_criteria, columns=['Criteria', 'Count'])
    fig_crit, ax_crit = plt.subplots()
    sns.barplot(x='Count', y='Criteria', data=crit_df, ax=ax_crit, palette='Greens_r')
    st.pyplot(fig_crit)

# --- Section: Heatmap ---
st.markdown('<div class="section" id="heatmap"></div>', unsafe_allow_html=True)
if {'COMPANY', 'LOCATION'}.issubset(df.columns):
    st.subheader("🌍 Heatmap: Companies Hiring by Location")
    heatmap_data = df.groupby(['COMPANY', 'LOCATION']).size().unstack(fill_value=0)
    fig_heat, ax_heat = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax_heat)
    ax_heat.set_xlabel("Location")
    ax_heat.set_ylabel("Company")
    st.pyplot(fig_heat)

# --- Section: WordCloud ---
st.markdown('<div class="section" id="wordcloud"></div>', unsafe_allow_html=True)
show_wc = st.checkbox("☁ Show Word Cloud from Descriptions")
if show_wc and 'DESCRIPTION' in df.columns:
    text = ' '.join(df['DESCRIPTION'].dropna().astype(str))
    wc = WordCloud(max_words=100, background_color='white').generate(text)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wc, interpolation='bilinear')
    ax_wc.axis("off")
    st.pyplot(fig_wc)

# --- Footer ---
st.markdown("---")
st.caption("Made by Saloni Pal | Data Source: LinkedIn")
