import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import spacy
import spacy.cli

# Load modules
from utils.pdf_reader import extract_text_from_pdf
from utils.docx_reader import extract_text_from_docx
from utils.parser import parse_resume
from utils.ats_score import calculate_ats_score
from utils.jd_match import match_job_description
from utils.summary import generate_summary
from utils.recommendations import generate_recommendations
from utils.charts import (
    create_ats_gauge,
    create_skills_chart,
    create_completeness_chart,
    create_jd_match_gauge,
    create_keyword_comparison_chart
)
from utils.report_generator import generate_pdf_report

# Ensure spaCy model is downloaded programmatically on startup
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        with st.spinner("Downloading NLP model (one-time setup, please wait)..."):
            spacy.cli.download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

load_spacy_model()

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer & ATS Score Checker",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple White & Blue Styling Injected via CSS
st.markdown("""
    <style>
        /* General Page Styling */
        .main {
            background-color: #FFFFFF;
        }
        
        /* Heading Styles */
        h1, h2, h3 {
            color: #1E3A8A !important;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
        }
        
        /* Metric Card styling */
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 3px solid #3B82F6;
            border-radius: 4px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .metric-title {
            color: #64748B;
            font-size: 13px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .metric-value {
            color: #1E3A8A;
            font-size: 24px;
            font-weight: 600;
            margin-top: 4px;
        }
        
        .metric-subtitle {
            color: #94A3B8;
            font-size: 11px;
            margin-top: 4px;
        }
        
        /* Highlight labels */
        .skill-badge {
            display: inline-block;
            background-color: #EFF6FF;
            color: #1E3A8A;
            border: 1px solid #BFDBFE;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin: 2px;
            font-weight: 500;
        }
        
        .missing-badge {
            display: inline-block;
            background-color: #FEF2F2;
            color: #991B1B;
            border: 1px solid #FCA5A5;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin: 2px;
            font-weight: 500;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- DATABASE HELPERS -----------------
CSV_PATH = "Resume.csv"

def log_analysis(name, email, score, match_pct, filename):
    """Logs the analyzed resume details to Resume.csv."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    match_str = f"{match_pct}%" if match_pct is not None else "N/A"
    
    new_row = pd.DataFrame([{
        "Timestamp": timestamp,
        "Name": name,
        "Email": email,
        "ATS_Score": int(score),
        "Match_Percentage": match_str,
        "Filename": filename
    }])
    
    if os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH)
            # Remove any header-like empty rows
            df = df.dropna(how='all')
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(CSV_PATH, index=False)
        except Exception:
            new_row.to_csv(CSV_PATH, index=False)
    else:
        new_row.to_csv(CSV_PATH, index=False)

def read_history():
    """Reads execution history from Resume.csv."""
    if os.path.exists(CSV_PATH):
        try:
            df = pd.read_csv(CSV_PATH)
            return df.sort_values(by="Timestamp", ascending=False)
        except Exception:
            return pd.DataFrame(columns=["Timestamp", "Name", "Email", "ATS_Score", "Match_Percentage", "Filename"])
    return pd.DataFrame(columns=["Timestamp", "Name", "Email", "ATS_Score", "Match_Percentage", "Filename"])

def clear_history():
    """Clears history from Resume.csv."""
    df = pd.DataFrame(columns=["Timestamp", "Name", "Email", "ATS_Score", "Match_Percentage", "Filename"])
    df.to_csv(CSV_PATH, index=False)

# ----------------- SESSION STATE SETUP -----------------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "ats_results" not in st.session_state:
    st.session_state.ats_results = None
if "jd_results" not in st.session_state:
    st.session_state.jd_results = None
if "filename" not in st.session_state:
    st.session_state.filename = ""
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

# ----------------- SIDEBAR NAVIGATION -----------------
st.sidebar.markdown(
    "<h2 style='text-align:center;'>AI Resume Analyzer</h2>", 
    unsafe_allow_html=True
)
st.sidebar.markdown("<hr/>", unsafe_allow_html=True)

nav_option = st.sidebar.radio(
    "NAVIGATION",
    ["Upload & Dashboard", "Detailed Assessment", "JD Matcher", "Recommendations", "History Log"]
)

st.sidebar.markdown("<br/><br/><br/>", unsafe_allow_html=True)
st.sidebar.markdown("<hr/>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<div style='color:#64748B; font-size:11px; text-align:center;'>"
    "Intelligent ATS Checker v1.0.0<br/>"
    "Created with Streamlit & spaCy"
    "</div>", 
    unsafe_allow_html=True
)

# ----------------- PAGE 1: UPLOAD & DASHBOARD -----------------
if nav_option == "Upload & Dashboard":
    st.title("AI-Powered Intelligent Resume Analyzer")
    st.write("Scan your resume structure, calculate ATS scores, extract categorized skills, and map compliance.")
    
    # 2-column layout: Upload tools and general status
    col_input, col_status = st.columns([3, 2])
    
    with col_input:
        st.markdown("### 1. Upload or Paste Resume")
        upload_mode = st.radio("Choose input method:", ["File Upload (PDF / DOCX)", "Manual Paste Text"])
        
        input_text = ""
        uploaded_file = None
        
        if upload_mode == "File Upload (PDF / DOCX)":
            uploaded_file = st.file_uploader("Upload Resume:", type=["pdf", "docx"])
            if uploaded_file is not None:
                # Store filename
                st.session_state.filename = uploaded_file.name
                
                # Extract text
                file_bytes = uploaded_file.read()
                try:
                    if uploaded_file.name.endswith(".pdf"):
                        input_text = extract_text_from_pdf(file_bytes)
                    elif uploaded_file.name.endswith(".docx"):
                        input_text = extract_text_from_docx(file_bytes)
                except Exception as e:
                    st.error(f"Error parsing file: {str(e)}")
        else:
            input_text = st.text_area("Paste resume text here:", height=250)
            st.session_state.filename = "Manually Pasted Text"
            
        analyze_clicked = st.button("RUN ANALYSIS")
        
        if analyze_clicked:
            if not input_text.strip():
                st.warning("Please upload a file or paste text to analyze.")
            else:
                with st.spinner("Analyzing resume structure and skills..."):
                    # Process
                    st.session_state.resume_text = input_text
                    parsed_data = parse_resume(input_text)
                    parsed_data["raw_text"] = input_text # save raw text reference
                    parsed_data["filename"] = st.session_state.filename
                    
                    st.session_state.parsed_data = parsed_data
                    
                    # Compute ATS Score
                    ats_results = calculate_ats_score(parsed_data, input_text)
                    st.session_state.ats_results = ats_results
                    
                    # If JD text already existed in state, refresh matcher
                    if st.session_state.jd_text.strip():
                        st.session_state.jd_results = match_job_description(input_text, st.session_state.jd_text)
                    else:
                        st.session_state.jd_results = None
                        
                    # Log into CSV history
                    log_analysis(
                        parsed_data["name"],
                        parsed_data["email"] if parsed_data["email"] else "N/A",
                        ats_results["total_score"],
                        st.session_state.jd_results["match_percentage"] if st.session_state.jd_results else None,
                        st.session_state.filename
                    )
                    
                    st.success("Resume analyzed successfully!")
                    
    with col_status:
        st.markdown("### 2. Live Core Status")
        if st.session_state.ats_results is not None:
            # Render Overall ATS Gauge
            score = st.session_state.ats_results["total_score"]
            st.plotly_chart(create_ats_gauge(score), use_container_width=True)
            
            # Basic stats summary
            word_count = st.session_state.ats_results["metrics"]["word_count"]
            skills_count = st.session_state.ats_results["metrics"]["skills_count"]
            
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Parsed Candidate</div>
                    <div class="metric-value">{st.session_state.parsed_data["name"]}</div>
                    <div class="metric-subtitle">Detected from document header</div>
                </div>
            """, unsafe_allow_html=True)
            
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Word Count</div>
                        <div class="metric-value">{word_count}</div>
                        <div class="metric-subtitle">Ideal: 400 - 800</div>
                    </div>
                """, unsafe_allow_html=True)
            with col_stat2:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-title">Total Skills</div>
                        <div class="metric-value">{skills_count}</div>
                        <div class="metric-subtitle">Identified across categories</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active analysis. Please upload your resume on the left panel to begin.")
            
    # Display details below if parsed
    if st.session_state.parsed_data is not None:
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("Parsed Contact Details")
        
        c_name, c_email, c_phone, c_linkedin, c_github = st.columns(5)
        
        with c_name:
            st.text_input("Name:", value=st.session_state.parsed_data["name"], disabled=True)
        with c_email:
            st.text_input("Email Address:", value=st.session_state.parsed_data["email"] or "Not Detected", disabled=True)
        with c_phone:
            st.text_input("Phone Number:", value=st.session_state.parsed_data["phone"] or "Not Detected", disabled=True)
        with c_linkedin:
            st.text_input("LinkedIn Profile:", value=st.session_state.parsed_data["linkedin"] or "Not Detected", disabled=True)
        with c_github:
            st.text_input("GitHub Profile:", value=st.session_state.parsed_data["github"] or "Not Detected", disabled=True)
            
        # Summary & PDF Download
        col_sum, col_rep = st.columns([3, 1])
        with col_sum:
            st.markdown("### Professional Summary (Extractive NLP)")
            sum_text = generate_summary(st.session_state.resume_text, st.session_state.parsed_data["skills"])
            st.info(sum_text)
        with col_rep:
            st.markdown("### Report Export")
            st.write("Generate a formal PDF containing ATS ratings, skill logs, and custom guidelines.")
            
            # Generate Report Bytes
            try:
                report_bytes = generate_pdf_report(
                    st.session_state.parsed_data,
                    st.session_state.ats_results,
                    st.session_state.jd_results
                )
                
                st.download_button(
                    label="DOWNLOAD PDF REPORT",
                    data=report_bytes,
                    file_name=f"ATS_Report_{st.session_state.parsed_data['name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error compiling report: {str(e)}")

# ----------------- PAGE 2: DETAILED ASSESSMENT -----------------
elif nav_option == "Detailed Assessment":
    st.title("Detailed ATS Assessment")
    
    if st.session_state.parsed_data is None:
        st.warning("Please upload a resume first to run detailed metrics.")
    else:
        # Layout: Left side charts, Right side section checkups
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.plotly_chart(create_completeness_chart(st.session_state.parsed_data["sections"]), use_container_width=True)
            st.plotly_chart(create_skills_chart(st.session_state.parsed_data["skills"]), use_container_width=True)
            
        with col_right:
            st.markdown("### ATS Breakdown")
            sub_scores = st.session_state.ats_results["sub_scores"]
            
            st.write(f"**Contact Information Completeness:** {sub_scores['contact_info']} / 15")
            st.progress(sub_scores['contact_info'] / 15)
            
            st.write(f"**Section Structuring & Content:** {sub_scores['completeness']} / 25")
            st.progress(sub_scores['completeness'] / 25)
            
            st.write(f"**Document Formatting & Word Count:** {sub_scores['formatting']} / 20")
            st.progress(sub_scores['formatting'] / 20)
            
            st.write(f"**Industry Keywords & Skills Density:** {sub_scores['skills']} / 20")
            st.progress(sub_scores['skills'] / 20)
            
            st.write(f"**Action Verbs / Business Impact:** {sub_scores['action_verbs']} / 20")
            st.progress(sub_scores['action_verbs'] / 20)
            
            # List structural positives and negatives
            st.markdown("### Evaluation Checklist")
            tab_pos, tab_neg = st.tabs(["Positives Detected", "Areas for Improvement"])
            
            with tab_pos:
                for pos in st.session_state.ats_results["positives"]:
                    st.write(f"- {pos}")
            with tab_neg:
                if st.session_state.ats_results["improvements"]:
                    for imp in st.session_state.ats_results["improvements"]:
                        st.write(f"- {imp}")
                else:
                    st.write("Excellent! No immediate formatting issues identified.")

        # Lower Panel: Raw parsed sections
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.subheader("Extracted Document Sections")
        
        sec_tabs = st.tabs(["Education", "Experience", "Projects", "Certifications", "Extracted Skills"])
        sections = st.session_state.parsed_data["sections"]
        
        with sec_tabs[0]:
            if sections["education"].strip():
                st.text_area("Education Text:", value=sections["education"], height=200, disabled=True)
            else:
                st.info("No education details detected. Try standardizing your heading to 'Education'.")
        with sec_tabs[1]:
            if sections["experience"].strip():
                st.text_area("Experience Text:", value=sections["experience"], height=200, disabled=True)
            else:
                st.info("No experience details detected. Try standardizing your heading to 'Work Experience'.")
        with sec_tabs[2]:
            if sections["projects"].strip():
                st.text_area("Projects Text:", value=sections["projects"], height=200, disabled=True)
            else:
                st.info("No projects details detected. Try standardizing your heading to 'Projects'.")
        with sec_tabs[3]:
            if sections["certifications"].strip():
                st.text_area("Certifications Text:", value=sections["certifications"], height=200, disabled=True)
            else:
                st.info("No certifications details detected. Try standardizing your heading to 'Certifications'.")
        with sec_tabs[4]:
            skills = st.session_state.parsed_data["skills"]
            for category, skill_list in skills.items():
                if skill_list:
                    st.write(f"**{category}:**")
                    badges = "".join(f"<span class='skill-badge'>{skill}</span>" for skill in skill_list)
                    st.markdown(badges, unsafe_allow_html=True)
                    st.write("")

# ----------------- PAGE 3: JD MATCHER -----------------
elif nav_option == "JD Matcher":
    st.title("Job Description Matcher")
    st.write("Paste a job description to calculate keyword match, similarity rating, and locate missing terms.")
    
    if st.session_state.resume_text == "":
        st.warning("Please upload a resume first under the Dashboard page.")
    else:
        col_jd, col_match = st.columns([3, 2])
        
        with col_jd:
            st.markdown("### Paste Job Description Details")
            jd_text = st.text_area(
                "Paste JD text here:", 
                value=st.session_state.jd_text, 
                height=300, 
                placeholder="We are looking for a Python Developer experienced in Django, AWS, Kubernetes, Postgres..."
            )
            
            match_clicked = st.button("RUN MATCH CHECK")
            
            if match_clicked and jd_text.strip():
                st.session_state.jd_text = jd_text
                with st.spinner("Calculating match statistics..."):
                    st.session_state.jd_results = match_job_description(st.session_state.resume_text, jd_text)
                    st.success("Calculations complete!")
                    
        with col_match:
            st.markdown("### Match Outcome")
            if st.session_state.jd_results is not None:
                match_pct = st.session_state.jd_results["match_percentage"]
                st.plotly_chart(create_jd_match_gauge(match_pct), use_container_width=True)
                
                # Check status text
                if match_pct >= 75:
                    st.success(f"**Strong Compatibility! ({match_pct}%)** Your resume matches a high density of skills and keywords.")
                elif match_pct >= 50:
                    st.info(f"**Moderate Compatibility. ({match_pct}%)** There is decent alignment, but you should add some of the missing keywords to improve indexing.")
                else:
                    st.warning(f"**Low Compatibility. ({match_pct}%)** Critical requirements or tools are missing from your resume.")
            else:
                st.info("Enter a Job Description on the left and run match check to see similarity gauge.")
                
        # Lower panel: Details of matched/missing keywords
        if st.session_state.jd_results is not None:
            st.markdown("<hr/>", unsafe_allow_html=True)
            st.subheader("Skill Alignments & Gaps")
            
            tab_matched, tab_missing = st.tabs(["Matched Skills", "Missing Skills (Recommended)"])
            
            with tab_matched:
                matched_skills = st.session_state.jd_results["matched_skills"]
                if matched_skills:
                    badges = "".join(f"<span class='skill-badge'>{skill}</span>" for skill in matched_skills)
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.write("No exact skills overlapped between the resume and job description.")
                    
            with tab_missing:
                missing_skills = st.session_state.jd_results["missing_skills"]
                if missing_skills:
                    st.write("Incorporate these missing skills mentioned in the job description to improve matching:")
                    badges = "".join(f"<span class='missing-badge'>{skill}</span>" for skill in missing_skills)
                    st.markdown(badges, unsafe_allow_html=True)
                else:
                    st.write("Awesome! You possess all specific skills referenced in this job description.")
                    
            # Display Plotly Keyword comparison
            st.markdown("<br/>", unsafe_allow_html=True)
            st.plotly_chart(create_keyword_comparison_chart(st.session_state.jd_results["keyword_analysis"]), use_container_width=True)

# ----------------- PAGE 4: RECOMMENDATIONS -----------------
elif nav_option == "Recommendations":
    st.title("Actionable Recommendations")
    st.write("Boost your ATS Score and recruiter success rates with structured formatting, content, and phrasing improvements.")
    
    if st.session_state.parsed_data is None:
        st.warning("Please upload a resume first to view recommendations.")
    else:
        recs = generate_recommendations(
            st.session_state.parsed_data,
            st.session_state.ats_results,
            st.session_state.jd_results
        )
        
        # Structure suggestions in 4 visual tabs
        tab_format, tab_content, tab_skills, tab_hacks = st.tabs([
            "Layout & Formatting", 
            "Phrasing & Content", 
            "Skills & Certifications", 
            "ATS Optimization Hacks"
        ])
        
        with tab_format:
            st.markdown("### Document Layout & Organization")
            if recs["formatting"]:
                for r in recs["formatting"]:
                    st.info(r)
            else:
                st.success("Your document format, length, and sections look fully optimized!")
                
        with tab_content:
            st.markdown("### Phrasing and Description Strength")
            if recs["content_strength"]:
                for r in recs["content_strength"]:
                    st.info(r)
            else:
                st.success("Your bullet points contain powerful action-oriented phrases and metrics!")
                
            # Add action verbs cheat-sheet
            st.markdown("<br/>", unsafe_allow_html=True)
            st.subheader("Action Verbs Cheat-Sheet")
            st.write("Start bullet descriptions with these impact terms to improve ATS readability and recruiter impressions:")
            verbs = ["Led", "Engineered", "Developed", "Optimized", "Spearheaded", "Automated", "Collaborated", "Resolved", "Created", "Achieved", "Launched", "Streamlined", "Formulated", "Supervised"]
            badges = "".join(f"<span class='skill-badge'>{verb}</span>" for verb in verbs)
            st.markdown(badges, unsafe_allow_html=True)
            
        with tab_skills:
            st.markdown("### Skills and Certification Enhancements")
            for r in recs["skills_certs"]:
                st.info(r)
                
        with tab_hacks:
            st.markdown("### Core ATS Optimization Advice")
            for r in recs["ats_hacks"]:
                st.warning(r)

# ----------------- PAGE 5: HISTORY LOG -----------------
elif nav_option == "History Log":
    st.title("Past Resume Analyses")
    st.write("Review, compare, and delete historical resume assessment metadata.")
    
    # Buttons to reset
    col_empty, col_clear = st.columns([4, 1])
    with col_clear:
        if st.button("CLEAR ALL HISTORY"):
            clear_history()
            st.success("History database wiped!")
            
    history_df = read_history()
    
    if history_df.empty:
        st.info("No past resume logs found. Once you complete your first scan, it will be saved here.")
    else:
        st.dataframe(history_df, use_container_width=True)
        
        # Display small statistics
        st.subheader("Summary Analytics")
        avg_score = history_df["ATS_Score"].mean()
        high_score = history_df["ATS_Score"].max()
        records_count = len(history_df)
        
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Total Evaluated</div>
                    <div class="metric-value">{records_count}</div>
                    <div class="metric-subtitle">Resumes logged in history</div>
                </div>
            """, unsafe_allow_html=True)
        with col_c2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Average ATS Rating</div>
                    <div class="metric-value">{avg_score:.1f}</div>
                    <div class="metric-subtitle">Out of 100 maximum score</div>
                </div>
            """, unsafe_allow_html=True)
        with col_c3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Highest ATS Score</div>
                    <div class="metric-value">{high_score}</div>
                    <div class="metric-subtitle">Best result logged so far</div>
                </div>
            """, unsafe_allow_html=True)
