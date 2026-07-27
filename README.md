<<<<<<< HEAD
# AI-Powered Intelligent Resume Analyzer & ATS Score Checker

A premium, professional AI-powered Intelligent Resume Analyzer web application built with Python and Streamlit. This offline-capable app parses resumes (PDF/DOCX/Text), extracts candidate metadata and categorizes technical/soft skills, calculates an ATS compliance score, matches alignment against custom job descriptions, generates executive summaries, provides actionable improvements, and exports visual PDF evaluation reports.

---

## Features

1. **Multi-Format Parsing**: Supports file uploads for `.pdf` and `.docx` or manual plain text copy-pasting.
2. **Dynamic Dashboard (White & Blue Theme)**: A modern, clean, user-friendly interface configured with visual cards, sidebar navigation, custom HSL blue gradients, and hover animations.
3. **Structured Entity Extraction**: Extract Candidate Name, Email, Phone, LinkedIn, and GitHub profile URLs.
4. **Categorized Skill Extraction**: Parses text using spaCy and regex mapping into 6 categories: Programming Languages, Frameworks, Databases, Cloud & DevOps, Tools, and Soft Skills.
5. **Multi-Criteria ATS Score (0-100)**: Evaluates resumes on contact info, sections completeness, ideal length, keywords density, and powerful action verb count.
6. **Semantic Job Description Matching**: Computes similarity using TF-IDF and skill alignment ratios. Displays matched vs. missing skills and a side-by-side keyword density chart.
7. **Executive Extractive Summary**: Utilizes term-frequency scoring to extract the top sentences representing professional experience.
8. **Actionable Recommendations**: Displays optimizations split into formatting, phrasing, skills/certs, and core ATS hacks.
9. **Analysis History Database (`Resume.csv`)**: Logs analyses to a local CSV database to compare stats, display tables, and calculate metrics (average score, best rating).
10. **Report Export (ReportLab PDF)**: Compiles metrics, summaries, tables of missing skills, and visual progress meters into a printable PDF report.

---

## Installation & Setup

Follow these steps to run the application locally on Windows:

### 1. Clone or Open Workspace
Ensure you are in the project folder:
```powershell
cd "c:\Users\user\OneDrive\Desktop\DA Project\Intelligent Resume Analyzer & ATS Score Checker"
```

### 2. Set Up a Virtual Environment (Recommended)
Create and activate a virtual environment:
```powershell
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install all required libraries from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
Start the Streamlit development server:
```powershell
streamlit run app.py
```
*Note: On first startup, the app will automatically download spaCy's `en_core_web_sm` model if it is not already available.*

---

## Project Structure

```
Intelligent Resume Analyzer & ATS Score Checker/
│
├── app.py                   # Main Streamlit web application entry point
├── requirements.txt         # Required python packages
├── README.md                # Project documentation
├── Resume.csv               # Local history tracking database
│
├── utils/
│   ├── pdf_reader.py        # PDF text parser using PyPDF2
│   ├── docx_reader.py       # DOCX text parser using python-docx
│   ├── parser.py            # Section separation and metadata extraction
│   ├── ats_score.py         # ATS multi-criteria score calculations
│   ├── skill_extractor.py   # spaCy/regex skill classification
│   ├── jd_match.py          # TF-IDF job description matcher
│   ├── summary.py           # NLP sentence ranker for resume summary
│   ├── recommendations.py   # Rules for tailored enhancements
│   ├── charts.py            # Plotly dashboards generator
│   └── report_generator.py  # ReportLab PDF report compiler
│
├── models/                  # Optional local model storage
├── assets/                  # Images or styling assets
└── reports/                 # Saved PDF reports export folder
```

---

## Sample Resumes for Testing
Below is a structured plain-text resume template that you can copy-paste into the analyzer to test all features:

### Test Resume Example
```text
JOHN DOE
Email: john.doe@email.com | Phone: (123) 456-7890
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

PROFESSIONAL SUMMARY
Results-driven Software Engineer with over 4 years of experience designing and deploying scalable web applications. Proven expertise in cloud migrations and API optimization.

WORK EXPERIENCE
Senior Developer | Tech Solutions Inc. | 2022 - Present
- Led the redevelopment of a legacy backend services system, migration to microservices, and deployment to AWS.
- Designed and built rest APIs using Python, FastAPI, and PostgreSQL, which optimized application response times by 35%.
- Automated CI/CD deployment pipelines using GitHub Actions and Docker, reducing deployment times by 40%.
- Managed and mentored a team of 3 junior developers on Agile practices and Git workflows.

Software Engineer | DevCorp | 2020 - 2022
- Engineered web services using Java, Spring Boot, and MySQL databases.
- Collaborated with product managers to deliver 5 high-priority feature integrations.
- Integrated Prometheus and Grafana monitoring tools to track infrastructure health.

PROJECTS
E-Commerce API Service (Personal Project)
- Developed a high-performance shopping cart backend using Go, Redis, and MongoDB.
- Containerized application services using Docker and deployed to AWS ECS.

EDUCATION
Bachelor of Science in Computer Science
University of Technology | 2016 - 2020

CERTIFICATIONS
- AWS Certified Solutions Architect - Associate
- Certified ScrumMaster (CSM)

SKILLS
- Programming Languages: Python, Java, Go, SQL, HTML, CSS, JavaScript
- Frameworks: FastAPI, Django, Spring Boot, React
- Databases: PostgreSQL, MySQL, Redis, MongoDB
- Cloud & DevOps: AWS, Docker, GitHub Actions, CI/CD, Prometheus, Grafana
- Tools: Git, GitHub, Jira, VS Code
- Soft Skills: Leadership, Collaboration, Agile, Problem Solving, Communication
```
=======
# AI-Resume-Analyzer
>>>>>>> 503488d8e27d6f161a033653950c24daeca9edfd
