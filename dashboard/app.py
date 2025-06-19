
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re

st.set_page_config(layout="wide", page_title="LinkedIn Job Dashboard", page_icon="🔍")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Pal-Saloni/linkedin-job-analysis/main/cleaned/cleaned_jobs.csv"
    return pd.read_csv(url)

df = load_data()

# --- Custom Navbar ---
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
    top: 125px;
    right: 20px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 12px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    padding: 10px 15px;
    z-index: 10000;
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
    animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}
.main > div:first-child {
    margin-top: 140px;
}
@media screen and (max-width: 768px) {
    .nav-icons {
        gap: 12px;
    }
    .logo {
        font-size: 20px;
    }
    .hamburger {
        font-size: 24px;
    }
}
</style>

<div class="navbar">
    <div class="logo">Saloni Pal</div>
    <div class="nav-icons">
        <a href="https://github.com/Pal-Saloni" target="_blank" title="GitHub Profile">🐱‍💻</a>
        <a href="https://www.linkedin.com/in/salonipal07/" target="_blank" title="LinkedIn Profile">💼</a>
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
    const dropdown = document.getElementById("navDropdown");
    dropdown.classList.toggle("show");
}
document.addEventListener("click", function (event) {
    const dropdown = document.getElementById("navDropdown");
    const button = event.target.closest(".hamburger");
    if (!dropdown.contains(event.target) && !button) {
        dropdown.classList.remove("show");
    }
});
document.querySelectorAll('.dropdown a').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 80,
                behavior: 'smooth'
            });
        }
        document.getElementById("navDropdown").classList.remove("show");
    });
});
</script>
""", unsafe_allow_html=True)
