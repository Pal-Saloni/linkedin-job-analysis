
# 📊 LinkedIn Job Listings Analysis

A data analysis project exploring job trends, skill demands, company hiring patterns, and remote work insights using LinkedIn job data from Africa.

---

## 🔍 Project Overview

This project performs **end-to-end analysis** of LinkedIn job listings — from raw data cleaning, exploratory visualizations, to skill extraction via text mining.

---

## 🗂️ Project Structure

```
linkedin-job-analysis/
│
├── data/                         # Raw dataset
│   └── linkedin-jobs-africa.xlsx
│
├── cleaned/                      # Cleaned version of the dataset
│   └── cleaned_jobs.csv
│
├── notebooks/                    # Jupyter Notebooks for analysis
│   └── 01-data-cleaning.ipynb
│   └── 02-eda-visualizations.ipynb
│   └── 03-text-analysis.ipynb
│
├── visuals/                      # Output charts, graphs, wordclouds
│   └── *.png, *.jpg
│
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 📌 Objectives

- Clean and preprocess job listing data
- Identify **top hiring companies**, **popular job titles**, and **key locations**
- Compare **remote vs. onsite** work patterns
- Extract **in-demand skills** from job descriptions
- Visualize insights with **charts** and **word clouds**

---

## 🧪 How to Run

1. Clone this repository:
```bash
git clone https://github.com/your-username/linkedin-job-analysis.git
cd linkedin-job-analysis
```

2. (Optional) Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required libraries:
```bash
pip install -r requirements.txt
```

4. Open the notebooks in order:
   - `01-data-cleaning.ipynb`
   - `02-eda-visualizations.ipynb`
   - `03-text-analysis.ipynb`

5. Output charts and graphics will be saved to `/visuals/`.

---

## 📈 Sample Visuals

- `top_companies.png` – Companies with most listings
- `job_titles.png` – Common job titles
- `remote_vs_onsite_pie.png` – Work type breakdown
- `wordcloud_skills.png` – Frequent skill terms

---

## 🛠️ Tech Stack

- Python 3.10+
- Jupyter Notebook
- `pandas`, `numpy` – Data manipulation
- `matplotlib`, `seaborn`, `plotly` – Visualizations
- `wordcloud`, `nltk`, `re` – Text mining

---

## 📬 Contact

Have questions, suggestions, or want to collaborate?

Feel free to connect on [LinkedIn](https://www.linkedin.com/in/saloni-pal-6b58352b4) or drop a message.

---

## ⭐ GitHub Tip

When uploading this project, ensure `.ipynb` files are present — GitHub renders them beautifully for demo purposes!
