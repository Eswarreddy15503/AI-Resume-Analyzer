import re
import logging

logger = logging.getLogger(__name__)

# List of powerful resume action verbs
ACTION_VERBS = [
    "led", "developed", "managed", "designed", "implemented", "optimized", "increased", 
    "reduced", "analyzed", "built", "engineered", "created", "spearheaded", "formulated", 
    "coordinated", "delivered", "executed", "collaborated", "facilitated", "improved", 
    "resolved", "integrated", "automated", "mentored", "supervised", "achieved", "launched"
]

def calculate_ats_score(parsed_data: dict, raw_text: str) -> dict:
    """
    Calculates the ATS (Applicant Tracking System) compatibility score of a resume.
    
    Args:
        parsed_data (dict): The dictionary returned by parse_resume.
        raw_text (str): The raw text of the resume.
        
    Returns:
        dict: Sub-scores, total score, and feedback (positives and improvements).
    """
    scores = {
        "contact_info": 0,
        "completeness": 0,
        "formatting": 0,
        "skills": 0,
        "action_verbs": 0
    }
    
    positives = []
    improvements = []
    
    # 1. Contact Information (Max: 15)
    contact_score = 0
    if parsed_data.get("name") and parsed_data["name"] != "Unknown":
        contact_score += 3
    else:
        improvements.append("Full Name was not clearly detected at the top of the resume.")
        
    if parsed_data.get("email"):
        contact_score += 4
    else:
        improvements.append("Email address is missing or not formatted correctly.")
        
    if parsed_data.get("phone"):
        contact_score += 4
    else:
        improvements.append("Phone number is missing or not formatted correctly.")
        
    if parsed_data.get("linkedin") or parsed_data.get("github"):
        contact_score += 4
        positives.append("Professional profile link (LinkedIn/GitHub) is present.")
    else:
        improvements.append("Add professional links like LinkedIn or GitHub to increase searchability.")
        
    if contact_score == 15:
        positives.append("All essential contact information is present.")
    scores["contact_info"] = contact_score
    
    # 2. Section Completeness (Max: 25)
    completeness_score = 0
    sections = parsed_data.get("sections", {})
    
    # Education: 5 points
    if len(sections.get("education", "").strip()) > 30:
        completeness_score += 5
        positives.append("Education section detected with sufficient details.")
    else:
        improvements.append("Education section is missing or lacks detail.")
        
    # Experience: 8 points
    if len(sections.get("experience", "").strip()) > 50:
        completeness_score += 8
        positives.append("Professional Experience section is well-structured.")
    else:
        improvements.append("Work Experience section is missing or too short.")
        
    # Skills: 4 points
    skills_extracted = sum(len(lst) for lst in parsed_data.get("skills", {}).values())
    if skills_extracted > 0:
        completeness_score += 4
        positives.append("Skills section parsed and categorized successfully.")
    else:
        improvements.append("Skills section is missing or could not be parsed.")
        
    # Projects: 4 points
    if len(sections.get("projects", "").strip()) > 40:
        completeness_score += 4
        positives.append("Projects section is present.")
    else:
        improvements.append("Add a Projects section to highlight hands-on experience.")
        
    # Certifications: 4 points
    if len(sections.get("certifications", "").strip()) > 20:
        completeness_score += 4
        positives.append("Certifications and Achievements are listed.")
    else:
        improvements.append("Add Certifications or Licenses to validate your skills.")
        
    scores["completeness"] = completeness_score
    
    # 3. Formatting & Length (Max: 20)
    formatting_score = 0
    words = raw_text.split()
    word_count = len(words)
    
    # Word count check: 10 points
    if 350 <= word_count <= 850:
        formatting_score += 10
        positives.append(f"Ideal resume length ({word_count} words).")
    elif 200 <= word_count < 350 or 850 < word_count <= 1200:
        formatting_score += 7
        improvements.append(f"Resume length is okay ({word_count} words), but aiming for 400-800 words is ideal.")
    else:
        formatting_score += 3
        improvements.append(f"Resume is either too short or too long ({word_count} words). Aim for a balanced 1-2 pages.")
        
    # Sentence length / complexity: 5 points
    sentences = re.split(r'[.!?]+', raw_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences:
        avg_sent_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sent_len <= 18:
            formatting_score += 5
            positives.append("Sentences are concise and easy to read.")
        elif avg_sent_len <= 25:
            formatting_score += 3
            improvements.append("Some sentences are slightly wordy. Try to write concise bullet points.")
        else:
            formatting_score += 1
            improvements.append("Average sentence length is high. Simplify sentences for better readability.")
    else:
        formatting_score += 3
        
    # Section clear headers: 5 points
    headers_detected = sum(1 for k, v in sections.items() if len(v.strip()) > 0)
    if headers_detected >= 4:
        formatting_score += 5
        positives.append("Clear section formatting and headers detected.")
    else:
        formatting_score += 2
        improvements.append("Ensure your section headers are standard (e.g. 'Work Experience' instead of custom titles).")
        
    scores["formatting"] = formatting_score
    
    # 4. Skills Quantity & Categories (Max: 20)
    skills_score = 0
    if skills_extracted >= 15:
        skills_score += 20
        positives.append(f"Strong keyword density with {skills_extracted} skills extracted.")
    elif 8 <= skills_extracted < 15:
        skills_score += 15
        positives.append(f"Good technical coverage with {skills_extracted} skills detected.")
    elif 3 <= skills_extracted < 8:
        skills_score += 10
        improvements.append("Add more technical keywords matching your field to pass automated ATS filters.")
    else:
        skills_score += 3
        improvements.append("Very few skills detected. List specific languages, tools, and methodologies.")
        
    scores["skills"] = skills_score
    
    # 5. Action Verbs (Max: 20)
    action_score = 0
    found_verbs = set()
    raw_lower = raw_text.lower()
    for verb in ACTION_VERBS:
        # Match word boundary
        if re.search(rf"\b{verb}\b", raw_lower):
            found_verbs.add(verb)
            
    verb_count = len(found_verbs)
    if verb_count >= 8:
        action_score += 20
        positives.append(f"Excellent use of strong action verbs ({verb_count} unique verbs).")
    elif 4 <= verb_count < 8:
        action_score += 15
        positives.append(f"Good use of professional action verbs ({verb_count} unique verbs).")
    elif 1 <= verb_count < 4:
        action_score += 10
        improvements.append("Use more impact action verbs (e.g., 'orchestrated', 'streamlined', 'optimized') at the start of bullet points.")
    else:
        action_score += 0
        improvements.append("No strong action verbs found. Replace phrases like 'responsible for' with action-oriented words.")
        
    scores["action_verbs"] = action_score
    
    # Total Score
    total_score = sum(scores.values())
    
    return {
        "sub_scores": scores,
        "total_score": min(total_score, 100),
        "positives": positives,
        "improvements": improvements,
        "metrics": {
            "word_count": word_count,
            "skills_count": skills_extracted,
            "action_verbs_count": verb_count
        }
    }
