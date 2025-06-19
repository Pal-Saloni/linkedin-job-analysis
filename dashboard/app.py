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
# (CSS code omitted for brevity — stays unchanged)

# --- Helper functions for layout style ---
def image_left_text_right(fig, heading, text):
    col1, col2 = st.columns([1.5, 2])
    with col1:
        st.pyplot(fig)
    with col2:
        st.subheader(heading)
        st.markdown(text)

def text_left_image_right(fig, heading, text):
    col1, col2 = st.columns([2, 1.5])
    with col1:
        st.subheader(heading)
        st.markdown(text)
    with col2:
        st.pyplot(fig)

# --- Sidebar Filters ---
with st.sidebar:
    st.header(">> Filter Jobs")
    location_filter = st.multiselect("📍 Select Location(s)", options=df['LOCATION'].dropna().unique())
    job_type_filter = st.multiselect("💼 Select Job Type(s)", options=df['ONSITE REMOTE'].dropna().unique())

if location_filter:
    df = df[df['LOCATION'].isin(location_filter)]
if job_type_filter:
    df = df[df['ONSITE REMOTE'].isin(job_type_filter)]

# --- Title ---
st.title("🔍 LinkedIn Job Market Dashboard")

# --- Key Metrics ---
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings", len(df))
col2.metric("Remote Jobs", df['ONSITE REMOTE'].str.contains("Remote", case=False, na=False).sum())
col3.metric("Top Hiring Location", df['LOCATION'].value_counts().idxmax())
st.divider()

# --- Top Job Titles ---
fig1, ax1 = plt.subplots()
df['TITLE'].value_counts().head(10).plot(kind='barh', color='#60a5fa', ax=ax1)
ax1.invert_yaxis()
ax1.set_xlabel("Count")
text_left_image_right(fig1, "💼 Top Job Titles", "Most frequently posted job titles across LinkedIn job listings.")

# --- Top Companies ---
fig2, ax2 = plt.subplots()
df['COMPANY'].value_counts().head(10).plot(kind='barh', color='#34d399', ax=ax2)
ax2.invert_yaxis()
ax2.set_xlabel("Count")
image_left_text_right(fig2, "🏢 Top Hiring Companies", "Companies hiring most frequently for tech/data roles.")

# --- Top Locations ---
fig3, ax3 = plt.subplots()
sns.barplot(x=df['LOCATION'].value_counts().head(10).values,
            y=df['LOCATION'].value_counts().head(10).index, palette="Blues_d", ax=ax3)
ax3.set_xlabel("Number of Jobs")
text_left_image_right(fig3, "📍 Top Job Locations", "Top cities/states where jobs are posted the most on LinkedIn.")

# --- Remote vs Onsite ---
remote_data = df['ONSITE REMOTE'].dropna().str.lower().value_counts()
fig4, ax4 = plt.subplots()
ax4.pie(remote_data, labels=remote_data.index, autopct='%1.1f%%', startangle=140)
ax4.axis("equal")
image_left_text_right(fig4, "🏠 Remote vs Onsite Jobs", "Distribution of jobs based on work setting — remote, onsite or hybrid.")

# --- Time Trends ---
if 'POSTED DATE' in df.columns:
    df['POSTED DATE'] = pd.to_datetime(df['POSTED DATE'], errors='coerce')
    trend = df.groupby(df['POSTED DATE'].dt.to_period('M')).size()
    fig5, ax5 = plt.subplots()
    trend.plot(ax=ax5, marker='o', color='orange')
    ax5.set_ylabel("Job Count")
    image_left_text_right(fig5, "🗕️ Job Postings Over Time", "Monthly trend of job postings based on LinkedIn data.")

# --- Weighted Score ---
if {'SALARY', 'TITLE', 'COMPANY', 'DESCRIPTION', 'ONSITE REMOTE', 'LOCATION', 'CRITERIA', 'POSTED DATE', 'LINK'}.issubset(df.columns):
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
    st.subheader("📈 Top Jobs by Weighted Score")
    st.dataframe(top_jobs[['TITLE', 'COMPANY', 'LOCATION', 'job_score']])

# --- Common Criteria ---
if 'CRITERIA' in df.columns:
    all_criteria = ' '.join(df['CRITERIA'].dropna()).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_criteria)
    common_criteria = Counter(words).most_common(10)
    crit_df = pd.DataFrame(common_criteria, columns=['Criteria', 'Count'])
    fig6, ax6 = plt.subplots()
    sns.barplot(x='Count', y='Criteria', data=crit_df, ax=ax6, palette='Greens_r')
    text_left_image_right(fig6, "📌 Most Common Job Criteria", "Top skills and qualifications frequently mentioned in job posts.")

# --- Heatmap ---
if {'COMPANY', 'LOCATION'}.issubset(df.columns):
    heatmap_data = df.groupby(['COMPANY', 'LOCATION']).size().unstack(fill_value=0)
    fig7, ax7 = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax7)
    ax7.set_xlabel("Location")
    ax7.set_ylabel("Company")
    image_left_text_right(fig7, "🌍 Heatmap: Hiring by Location & Company", "Visual correlation between companies and their active hiring locations.")

# --- WordCloud ---
show_wc = st.checkbox("☕ Show Word Cloud from Descriptions")
if show_wc and 'DESCRIPTION' in df.columns:
    text = ' '.join(df['DESCRIPTION'].dropna().astype(str))
    wc = WordCloud(max_words=100, background_color='white').generate(text)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wc, interpolation='bilinear')
    ax_wc.axis("off")
    image_left_text_right(fig_wc, "☁ Word Cloud from Job Descriptions", "Frequently used words in job descriptions across all listings.")

# --- Footer ---
st.markdown("---")
st.caption("Made by Saloni Pal | Data Source: LinkedIn")
