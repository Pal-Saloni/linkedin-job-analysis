import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re

st.set_page_config(layout="wide", page_title="LinkedIn Job Dashboard", page_icon="🔍")

# --- Load Data ---
@st.cache_data

def load_data():
    url = "https://raw.githubusercontent.com/Pal-Saloni/linkedin-job-analysis/main/cleaned/cleaned_jobs.csv"
    return pd.read_csv(url)

df = load_data()

# --- Inject Custom CSS for Modern Navbar, Glass Effect, and Dark Theme ---
st.markdown("""
<style>
/* App Background */
body, .main, .block-container {
  background: #0f172a;
  color: white;
  font-family: 'Segoe UI', sans-serif;
}

/* Navbar with glass effect */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background: rgba(30, 64, 175, 0.6); /* Glass blue */
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  color: white;
  font-weight: bold;
}

.logo {
  font-size: 1.5rem;
  font-family: 'Cursive';
  color: white;
  animation: slideInLeft 1s ease;
}

.nav-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #cbd5e1;
}

.hamburger {
  display: none;
  flex-direction: column;
  cursor: pointer;
  margin-left: 1rem;
}

.hamburger div {
  width: 25px;
  height: 3px;
  background-color: white;
  margin: 4px 0;
  transition: 0.4s;
}

.menu {
  display: none;
  flex-direction: column;
  position: fixed;
  top: 60px;
  right: 0;
  background-color: rgba(30, 64, 175, 0.9);
  backdrop-filter: blur(8px);
  padding: 1rem;
  z-index: 9998;
  border-radius: 0 0 0 10px;
}

.menu a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 0;
}

.show {
  display: flex !important;
}

@media screen and (max-width: 768px) {
  .nav-right {
    display: none;
  }
  .hamburger {
    display: flex;
  }
}
</style>

<script>
function toggleMenu() {
  const menu = document.querySelector('.menu');
  menu.classList.toggle('show');
}
</script>

<div class="navbar">
  <div class="logo">Saloni Pal</div>
  <div class="nav-right">
    <a class="nav-link" href="https://www.linkedin.com/in/saloni-pal-6b58352b4" target="_blank">LinkedIn</a>
    <a class="nav-link" href="https://github.com/Pal-Saloni" target="_blank">GitHub</a>
    <div class="hamburger" onclick="toggleMenu()">
      <div></div><div></div><div></div>
    </div>
  </div>
</div>

<div class="menu">
  <a href="#">Home</a>
  <a href="#">Top Titles</a>
  <a href="#">Top Companies</a>
  <a href="#">Remote Jobs</a>
  <a href="https://www.linkedin.com/in/saloni-pal-6b58352b4" target="_blank">LinkedIn</a>
  <a href="https://github.com/Pal-Saloni" target="_blank">GitHub</a>
</div>

<br><br><br><br>
""", unsafe_allow_html=True)

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

# --- Key Metrics ---
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings", len(df))
col2.metric("Remote Jobs", df['ONSITE REMOTE'].str.contains("Remote", case=False, na=False).sum())
col3.metric("Top Hiring Location", df['LOCATION'].value_counts().idxmax())
st.divider()

# --- Top Job Titles ---
st.subheader("💼 Top Job Titles")
st.bar_chart(df['TITLE'].value_counts().head(10))

# --- Top Companies ---
st.subheader("🏢 Top Hiring Companies")
st.bar_chart(df['COMPANY'].value_counts().head(10))

# --- Top Job Locations ---
st.subheader("📍 Top Job Locations")
fig, ax = plt.subplots()
sns.barplot(x=df['LOCATION'].value_counts().head(10).values,
            y=df['LOCATION'].value_counts().head(10).index, palette="Blues_d", ax=ax)
ax.set_xlabel("Number of Jobs")
ax.set_ylabel("")
st.pyplot(fig)

# --- Remote vs Onsite ---
st.subheader("🏠 Remote vs Onsite Jobs")
remote_data = df['ONSITE REMOTE'].dropna().str.lower().value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(remote_data, labels=remote_data.index, autopct='%1.1f%%', startangle=140)
ax2.axis("equal")
st.pyplot(fig2)

# --- Time Trends ---
if 'POSTED DATE' in df.columns:
    st.subheader("🗕️ Job Postings Over Time")
    df['POSTED DATE'] = pd.to_datetime(df['POSTED DATE'], errors='coerce')
    trend = df.groupby(df['POSTED DATE'].dt.to_period('M')).size()
    st.line_chart(trend)

# --- Weighted Job Score ---
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

# --- Most Common Criteria ---
if 'CRITERIA' in df.columns:
    st.subheader("📌 Most Common Criteria in Job Posts")
    all_criteria = ' '.join(df['CRITERIA'].dropna()).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_criteria)
    common_criteria = Counter(words).most_common(10)
    crit_df = pd.DataFrame(common_criteria, columns=['Criteria', 'Count'])
    fig_crit, ax_crit = plt.subplots()
    sns.barplot(x='Count', y='Criteria', data=crit_df, ax=ax_crit, palette='Greens_r')
    st.pyplot(fig_crit)

# --- Heatmap ---
if {'COMPANY', 'LOCATION'}.issubset(df.columns):
    st.subheader("🌍 Heatmap: Companies Hiring by Location")
    heatmap_data = df.groupby(['COMPANY', 'LOCATION']).size().unstack(fill_value=0)
    fig_heat, ax_heat = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax_heat)
    ax_heat.set_xlabel("Location")
    ax_heat.set_ylabel("Company")
    st.pyplot(fig_heat)

# --- WordCloud ---
show_wc = st.checkbox("☕ Show Word Cloud from Descriptions")
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
