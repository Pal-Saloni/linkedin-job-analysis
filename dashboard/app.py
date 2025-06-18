import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide", page_title="LinkedIn Job Dashboard")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("../cleaned/cleaned_jobs.csv")

df = load_data()

# Title
st.title("🔍 LinkedIn Job Market Dashboard")

# --- KPIs ---
st.markdown("### 📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings", len(df))
col2.metric("Remote Jobs", df['job_type'].str.contains("Remote", case=False, na=False).sum())
col3.metric("Top Hiring Location", df['location'].value_counts().idxmax())

st.divider()

# --- Top Job Titles ---
st.subheader("💼 Top Job Titles")
top_titles = df['job_title'].value_counts().head(10)
st.bar_chart(top_titles)

# --- Top Companies ---
st.subheader("🏢 Top Hiring Companies")
top_companies = df['company_name'].value_counts().head(10)
st.bar_chart(top_companies)

# --- Location Chart ---
st.subheader("📍 Top Job Locations")
top_locations = df['location'].value_counts().head(10)
fig, ax = plt.subplots()
sns.barplot(x=top_locations.values, y=top_locations.index, ax=ax, palette="Blues_d")
ax.set_xlabel("Number of Jobs")
st.pyplot(fig)

# --- Remote vs Onsite ---
st.subheader("🏠 Remote vs Onsite Jobs")
remote_data = df['job_type'].dropna().str.lower().value_counts()
fig2, ax2 = plt.subplots()
ax2.pie(remote_data, labels=remote_data.index, autopct='%1.1f%%', startangle=140)
ax2.axis("equal")
st.pyplot(fig2)

# --- Date Trends ---
if 'post_date' in df.columns:
    st.subheader("📅 Job Postings Over Time")
    df['post_date'] = pd.to_datetime(df['post_date'], errors='coerce')
    time_trend = df.groupby(df['post_date'].dt.to_period('M')).size()
    st.line_chart(time_trend)

# --- Description WordCloud (Optional) ---
show_wc = st.checkbox("Show Word Cloud from Job Descriptions")
if show_wc and 'description' in df.columns:
    from wordcloud import WordCloud
    text = ' '.join(df['description'].dropna())
    wc = WordCloud(max_words=100, background_color='white').generate(text)
    fig_wc, ax_wc = plt.subplots()
    ax_wc.imshow(wc, interpolation='bilinear')
    ax_wc.axis("off")
    st.pyplot(fig_wc)

st.markdown("---")
st.caption("Made by Saloni Pal | Data Source : LinkedIn")