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

# --- Custom CSS & JS for Navbar ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Pacifico&display=swap');

        .navbar {
            position: fixed;
            top: 60px;
            left: 0;
            right: 0;
            height: 65px;
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            z-index: 9999;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 1.5rem;
            flex-wrap: wrap;
        }

        .logo {
            font-family: 'Pacifico', cursive;
            font-size: 24px;
            color: #1f2937;
        }

        .nav-icons {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .nav-icons a {
            text-decoration: none;
            color: #1f2937;
            font-size: 20px;
        }

        .nav-icons a:hover {
            color: #2563eb;
        }

        .hamburger {
            font-size: 26px;
            cursor: pointer;
        }

        .dropdown {
            display: none;
            position: absolute;
            top: 65px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            padding: 10px 15px;
            z-index: 9999;
        }

        .dropdown a {
            display: block;
            margin: 8px 0;
            text-decoration: none;
            color: #1f2937;
            font-weight: 500;
        }

        .dropdown a:hover {
            color: #2563eb;
        }

        .dropdown.show {
            display: block;
        }

        .main > div:first-child {
            margin-top: 80px;
        }

        @media screen and (max-width: 768px) {
            .nav-icons {
                gap: 10px;
            }

            .logo {
                font-size: 20px;
            }
        }

        .search-input {
            padding: 4px 8px;
            border-radius: 6px;
            border: 1px solid #ccc;
            font-size: 14px;
        }
    </style>

    <div class="navbar">
        <div class="logo">Saloni Pal</div>
        <div class="nav-icons">
            <input type="text" id="searchInput" class="search-input" placeholder="Search section... 🔍" title="Search for section name">
            <a href="https://github.com/Pal-Saloni" target="_blank" title="GitHub Profile">Github</a>
            <a href="https://www.linkedin.com/in/salonipal07/" target="_blank" title="LinkedIn Profile">Linkedin</a>
            <div class="hamburger" onclick="toggleDropdown()">☰</div>
        </div>
        <div class="dropdown" id="navDropdown">
            <a href="#top-jobs">Top Job Titles</a>
            <a href="#top-companies">Top Companies</a>
            <a href="#top-locations">Top Locations</a>
            <a href="#remote-onsite">Remote vs Onsite</a>
            <a href="#time-trends">Job Trends</a>
            <a href="#weighted-score">Top Jobs</a>
            <a href="#common-criteria">Common Criteria</a>
            <a href="#heatmap">Heatmap</a>
            <a href="#wordcloud">WordCloud</a>
        </div>
    </div>

    <script>
        function toggleDropdown() {
            var dropdown = document.getElementById("navDropdown");
            dropdown.classList.toggle("show");
        }

        document.querySelectorAll('.dropdown a').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    window.scrollTo({
                        top: target.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            });
        });

        // Optional: Simple search box filter
        document.getElementById("searchInput").addEventListener("keyup", function () {
            var filter = this.value.toLowerCase();
            var links = document.querySelectorAll(".dropdown a");
            links.forEach(link => {
                if (link.textContent.toLowerCase().includes(filter)) {
                    link.style.display = "block";
                } else {
                    link.style.display = "none";
                }
            });
        });
    </script>
""", unsafe_allow_html=True)

# --- Helper Layout Functions ---
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

# --- Title & Metrics ---
st.title("🔍 LinkedIn Job Market Dashboard")
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Job Postings", len(df))
col2.metric("Remote Jobs", df['ONSITE REMOTE'].str.contains("Remote", case=False, na=False).sum())
col3.metric("Top Hiring Location", df['LOCATION'].value_counts().idxmax())
st.divider()

# --- Section: Top Job Titles ---
st.markdown('<a name="top-jobs"></a>', unsafe_allow_html=True)
fig1, ax1 = plt.subplots()
df['TITLE'].value_counts().head(10).plot(kind='barh', color='#60a5fa', ax=ax1)
ax1.invert_yaxis()
ax1.set_xlabel("Count")
text_left_image_right(fig1, "💼 Top Job Titles", "Most frequently posted job titles across LinkedIn job listings.")

# --- Section: Top Companies ---
st.markdown('<a name="top-companies"></a>', unsafe_allow_html=True)
fig2, ax2 = plt.subplots()
df['COMPANY'].value_counts().head(10).plot(kind='barh', color='#34d399', ax=ax2)
ax2.invert_yaxis()
ax2.set_xlabel("Count")
image_left_text_right(fig2, "🏢 Top Hiring Companies", "Companies hiring most frequently for tech/data roles.")

# --- Section: Top Locations ---
st.markdown('<a name="top-locations"></a>', unsafe_allow_html=True)
fig3, ax3 = plt.subplots()
sns.barplot(x=df['LOCATION'].value_counts().head(10).values,
            y=df['LOCATION'].value_counts().head(10).index, palette="Blues_d", ax=ax3)
ax3.set_xlabel("Number of Jobs")
text_left_image_right(fig3, "📍 Top Job Locations", "Top cities/states where jobs are posted the most on LinkedIn.")

# --- Section: Remote vs Onsite ---
st.markdown('<a name="remote-onsite"></a>', unsafe_allow_html=True)
remote_data = df['ONSITE REMOTE'].dropna().str.lower().value_counts()
fig4, ax4 = plt.subplots()
ax4.pie(remote_data, labels=remote_data.index, autopct='%1.1f%%', startangle=140)
ax4.axis("equal")
image_left_text_right(fig4, "🏠 Remote vs Onsite Jobs", "Distribution of jobs based on work setting — remote, onsite or hybrid.")

# --- Section: Time Trends ---
st.markdown('<a name="time-trends"></a>', unsafe_allow_html=True)
if 'POSTED DATE' in df.columns:
    df['POSTED DATE'] = pd.to_datetime(df['POSTED DATE'], errors='coerce')
    trend = df.groupby(df['POSTED DATE'].dt.to_period('M')).size()
    fig5, ax5 = plt.subplots()
    trend.plot(ax=ax5, marker='o', color='orange')
    ax5.set_ylabel("Job Count")
    image_left_text_right(fig5, "🗕️ Job Postings Over Time", "Monthly trend of job postings based on LinkedIn data.")

# --- Section: Weighted Score ---
st.markdown('<a name="weighted-score"></a>', unsafe_allow_html=True)
if {'SALARY', 'TITLE', 'COMPANY', 'DESCRIPTION', 'ONSITE REMOTE', 'LOCATION', 'CRITERIA', 'POSTED DATE', 'LINK'}.issubset(df.columns):
    df['job_score'] = (
        df['SALARY'].fillna(0).astype(str).str.len() * 1.0 +
        df['TITLE'].fillna(0).astype(str).str.len() * 0.5 +
        df['COMPANY'].fillna(0).astype(str).str.len() * 0.5 +
        df['DESCRIPTION'].fillna(0).astype(str).str.len() * 0.5 +
        df['ONSITE REMOTE'].fillna(0).astype(str).str.len() * 0.5 +
        df['LOCATION'].fillna(0).astype(str).str.len() * 0.5 +
        df['CRITERIA'].fillna(0).astype(str).str.len() * 0.5
    )
    top_jobs = df.sort_values("job_score", ascending=False).head(10)
    st.subheader("📈 Top Jobs by Weighted Score")
    st.dataframe(top_jobs[['TITLE', 'COMPANY', 'LOCATION', 'job_score']])

# --- Section: Common Criteria ---
st.markdown('<a name="common-criteria"></a>', unsafe_allow_html=True)
if 'CRITERIA' in df.columns:
    all_criteria = ' '.join(df['CRITERIA'].dropna()).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_criteria)
    common_criteria = Counter(words).most_common(10)
    crit_df = pd.DataFrame(common_criteria, columns=['Criteria', 'Count'])
    fig6, ax6 = plt.subplots()
    sns.barplot(x='Count', y='Criteria', data=crit_df, ax=ax6, palette='Greens_r')
    text_left_image_right(fig6, "📌 Most Common Job Criteria", "Top skills and qualifications frequently mentioned in job posts.")

# --- Section: Heatmap ---
st.markdown('<a name="heatmap"></a>', unsafe_allow_html=True)
if {'COMPANY', 'LOCATION'}.issubset(df.columns):
    heatmap_data = df.groupby(['COMPANY', 'LOCATION']).size().unstack(fill_value=0)
    fig7, ax7 = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", ax=ax7)
    ax7.set_xlabel("Location")
    ax7.set_ylabel("Company")
    image_left_text_right(fig7, "🌍 Heatmap: Hiring by Location & Company", "Visual correlation between companies and their active hiring locations.")

# --- Section: WordCloud ---
st.markdown('<a name="wordcloud"></a>', unsafe_allow_html=True)
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
