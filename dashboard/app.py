import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="LinkedIn Job Dashboard")

# --- Load Data ---
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Pal-Saloni/linkedin-job-analysis/main/cleaned/cleaned_jobs.csv"
    return pd.read_csv(url)

df = load_data()

# --- Apply Weights and Scoring ---
weights = {
    'salary': 1.0,
    'title': 0.5,
    'company_name': 0.5,
    'description': 0.5,
    'job_type': 0.5,         # corresponds to ONSITE REMOTE
    'location': 0.5,
    'criteria': 0.5,
    'post_date': 0.5,
    'link': 0.5,
}

def compute_score(row):
    score = 0
    if 'salary' in row and pd.notna(row['salary']):
        score += weights['salary']
    if 'job_type' in row and "remote" in str(row['job_type']).lower():
        score += weights['job_type']
    if 'title' in row and pd.notna(row['title']):
        score += weights['title']
    if 'company_name' in row and pd.notna(row['company_name']):
        score += weights['company_name']
    if 'description' in row and pd.notna(row['description']):
        score += weights['description']
    if 'location' in row and pd.notna(row['location']):
        score += weights['location']
    if 'criteria' in row and pd.notna(row['criteria']):
        score += weights['criteria']
    if 'post_date' in row and pd.notna(row['post_date']):
        score += weights['post_date']
    if 'link' in row and pd.notna(row['link']):
        score += weights['link']
    return score

df['score'] = df.apply(compute_score, axis=1)

# --- Dashboard Title ---
st.title("🔍 LinkedIn Job Market Dashboard")

# --- KPIs ---
st.markdown("### 📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings", len(df))
if 'job_type' in df.columns:
    col2.metric("Remote Jobs", df['job_type'].str.contains("Remote", case=False, na=False).sum())
else:
    col2.metric("Remote Jobs", "N/A")
col3.metric("Top Hiring Location", df['location'].value_counts().idxmax() if 'location' in df.columns else "N/A")

st.divider()

# --- Top Job Titles ---
if 'title' in df.columns:
    st.subheader("💼 Top Job Titles")
    top_titles = df['title'].value_counts().head(10)
    st.bar_chart(top_titles)

# --- Top Companies ---
if 'company_name' in df.columns:
    st.subheader("🏢 Top Hiring Companies")
    top_companies = df['company_name'].value_counts().head(10)
    st.bar_chart(top_companies)

# --- Location Chart ---
if 'location' in df.columns:
    st.subheader("📍 Top Job Locations")
    top_locations = df['location'].value_counts().head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=top_locations.values, y=top_locations.index, ax=ax, palette="Blues_d")
    ax.set_xlabel("Number of Jobs")
    st.pyplot(fig)

# --- Remote vs Onsite Pie ---
if 'job_type' in df.columns:
    st.subheader("🏠 Remote vs Onsite Jobs")
    remote_data = df['job_type'].dropna().str.lower().value_counts()
    fig2, ax2 = plt.subplots()
    ax2.pie(remote_data, labels=remote_data.index, autopct='%1.1f%%', startangle=140)
    ax2.axis("equal")
    st.pyplot(fig2)

# --- Date Trend Line ---
if 'post_date' in df.columns:
    st.subheader("📅 Job Postings Over Time")
    df['post_date'] = pd.to_datetime(df['post_date'], errors='coerce')
    time_trend = df.groupby(df['post_date'].dt.to_period('M')).size()
    st.line_chart(time_trend)

# --- WordCloud ---
show_wc = st.checkbox("Show Word Cloud from Job Descriptions")
if show_wc and 'description' in df.columns:
    from wordcloud import WordCloud
    text = ' '.join(df['description'].dropna())
    wc = WordCloud(max_words=100, background_color='white').generate(text)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wc, interpolation='bilinear')
    ax_wc.axis("off")
    st.pyplot(fig_wc)

# --- Top Scored Jobs Table ---
st.subheader("⭐ Top Scored Jobs")
st.dataframe(df.sort_values(by='score', ascending=False).head(10))

st.markdown("---")
st.caption("Made by Saloni Pal | Data Source: LinkedIn")
