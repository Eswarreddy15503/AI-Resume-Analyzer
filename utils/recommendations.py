import re
import logging

logger = logging.getLogger(__name__)

def generate_recommendations(parsed_data: dict, ats_results: dict, jd_results: dict = None) -> dict:
    """
    Generates a structured list of actionable recommendations for resume optimization.
    
    Args:
        parsed_data (dict): Parsed resume.
        ats_results (dict): Results of ATS score calculations.
        jd_results (dict, optional): Results from Job Description match if available.
        
    Returns:
        dict: Categorized recommendations.
    """
    recommendations = {
        "formatting": [],
        "content_strength": [],
        "skills_certs": [],
        "ats_hacks": []
    }
    
    # 1. Formatting & Structure Suggestions
    word_count = ats_results["metrics"]["word_count"]
    if word_count < 300:
        recommendations["formatting"].append(
            "Your resume is quite brief. Expand your descriptions of projects and professional experience to reach a target range of 400-800 words."
        )
    elif word_count > 1000:
        recommendations["formatting"].append(
            "Your resume is very long. Condense your sentences and focus only on relevant achievements to keep it under 2 pages (ideal word count: 400-800)."
        )
        
    sections = parsed_data.get("sections", {})
    if not sections.get("projects"):
        recommendations["formatting"].append(
            "Add a 'Projects' section. Practical projects are a strong indicator of technical capability, especially for developer and analyst roles."
        )
    if not sections.get("certifications"):
        recommendations["formatting"].append(
            "Add a 'Certifications' section to list professional licenses, courses, and credentials."
        )
        
    # Check if contact details are missing
    if not parsed_data.get("linkedin"):
        recommendations["formatting"].append(
            "LinkedIn Profile Link is missing. 85%+ of recruiters look for a LinkedIn profile link next to contact details."
        )
    if not parsed_data.get("github") and len(parsed_data.get("skills", {}).get("Programming Languages", [])) > 0:
        recommendations["formatting"].append(
            "GitHub Link is missing. For technical roles, linking a clean GitHub profile with portfolio code is highly recommended."
        )
        
    # 2. Content & Project Strength Suggestions
    action_verb_count = ats_results["metrics"]["action_verbs_count"]
    if action_verb_count < 5:
        recommendations["content_strength"].append(
            f"Increase impact verb density. You used only {action_verb_count} action-oriented verbs. Start your experience bullets with strong verbs like 'engineered', 'led', 'spearheaded'."
        )
        
    # Look for metrics / numbers in bullet points (e.g. %, $, numbers)
    raw_text = "".join(sections.values())
    metrics_match = re.findall(r"\b(\d+%\b|\d+\s*percent|\$\d+[\d,]*|\b\d+\s*(?:million|billion|k|x)\b)", raw_text, re.IGNORECASE)
    if len(metrics_match) < 3:
        recommendations["content_strength"].append(
            "Quantify your accomplishments. Recruiter screens favor resumes that use metrics. Instead of 'Optimized API response time', write 'Optimized API response time, reducing latency by 35% and increasing server throughput.'"
        )
    else:
        recommendations["content_strength"].append(
            "Great job! You have included metrics in your resume. Keep highlighting numeric outcomes to prove your business impact."
        )
        
    # Check for passive phrases
    passive_phrases = ["responsible for", "duties included", "helped in", "assisted with", "worked on"]
    found_passives = [phrase for phrase in passive_phrases if phrase in raw_text.lower()]
    if found_passives:
        recommendations["content_strength"].append(
            f"Replace passive phrases like '{found_passives[0]}' with direct, result-oriented statements. Write 'Orchestrated deployment of...' instead of 'Was responsible for deployment of...'"
        )
        
    # 3. Skills and Certifications Suggestions
    if jd_results and jd_results.get("missing_skills"):
        missing = jd_results["missing_skills"][:5] # show top 5
        recommendations["skills_certs"].append(
            f"The job description requests skills missing from your resume: {', '.join(missing)}. Integrate these technologies in your Skills section."
        )
    else:
        recommendations["skills_certs"].append(
            "Ensure you list core programming languages and database tools separately from general soft skills for easier parsing."
        )
        
    # General certification advice
    skills_categories = parsed_data.get("skills", {})
    languages = skills_categories.get("Programming Languages", [])
    cloud = skills_categories.get("Cloud & DevOps", [])
    
    if len(cloud) == 0:
        recommendations["skills_certs"].append(
            "Consider gaining cloud competency. Adding an entry-level certificate like AWS Cloud Practitioner, Azure Fundamentals, or GCP Digital Leader will expand your appeal."
        )
    else:
        recommendations["skills_certs"].append(
            "To solidify your cloud skills, consider seeking professional certifications (e.g., AWS Certified Solutions Architect, Azure Administrator)."
        )
        
    if "Agile" not in skills_categories.get("Soft Skills", []) and "Scrum" not in skills_categories.get("Soft Skills", []):
        recommendations["skills_certs"].append(
            "Add methodology skills if applicable: Mentioning Agile, Scrum, or Kanban demonstrates familiarity with modern software workflows."
        )
        
    # 4. ATS Hacks and Optimization Tips
    recommendations["ats_hacks"].append(
        "Avoid Placing Contact Information in Headers/Footers: ATS parsers often ignore header and footer sections. Place your name, email, and phone at the top of the body page."
    )
    recommendations["ats_hacks"].append(
        "Do not use charts, graphs, shapes, or multi-column text boxes in your PDF: ATS systems read top-to-bottom and left-to-right. Complex graphic tables will scramble your text."
    )
    recommendations["ats_hacks"].append(
        "Use standard font selections: Stick to safe, modern fonts (Arial, Calibri, Helvetica, Georgia) instead of custom decorative fonts."
    )
    recommendations["ats_hacks"].append(
        "Save and upload as a searchable PDF: Make sure you do not upload scanned images or print-to-pdf scans. Highlightable text is required for ATS matching."
    )
    
    return recommendations
