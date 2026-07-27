import re
import spacy
import logging
from utils.skill_extractor import extract_skills

logger = logging.getLogger(__name__)

# Section synonyms
SECTION_HEADERS = {
    "education": ["education", "academic background", "academic details", "qualifications", "academic history", "academic qualification", "studies", "academic profile"],
    "experience": ["experience", "work experience", "professional experience", "employment history", "work history", "career history", "professional background", "employment"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "technical projects", "recent projects", "project experience", "selected projects"],
    "certifications": ["certifications", "licenses", "credentials", "achievements", "courses", "awards", "publications", "certifications & licenses"],
    "skills": ["skills", "technical skills", "core competencies", "key skills", "skills & abilities", "skills and technologies", "technologies", "professional skills"]
}

# Regex patterns
EMAIL_REGEX = r"[\w\.-]+@[\w\.-]+\.\w+"
# Match standard formats like: +1-234-567-8901, (123) 456-7890, 1234567890, etc.
PHONE_REGEX = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
LINKEDIN_REGEX = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-\_]+/?\b"
GITHUB_REGEX = r"(?:https?://)?(?:www\.)?github\.com/[\w\-\_]+/?\b"

def parse_resume(text: str) -> dict:
    """
    Parses resume text to extract metadata and section content.
    
    Args:
        text (str): Raw resume text.
        
    Returns:
        dict: Parsed resume details.
    """
    # 1. Base Structure
    parsed_data = {
        "name": "Unknown",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "sections": {
            "education": "",
            "experience": "",
            "projects": "",
            "certifications": "",
            "skills_raw": ""
        },
        "skills": {}
    }
    
    if not text or not text.strip():
        return parsed_data
        
    # Extract Email
    email_match = re.search(EMAIL_REGEX, text)
    if email_match:
        parsed_data["email"] = email_match.group(0)
        
    # Extract Phone
    phone_match = re.search(PHONE_REGEX, text)
    if phone_match:
        parsed_data["phone"] = phone_match.group(0)
        
    # Extract LinkedIn
    linkedin_match = re.search(LINKEDIN_REGEX, text, re.IGNORECASE)
    if linkedin_match:
        parsed_data["linkedin"] = linkedin_match.group(0)
        
    # Extract GitHub
    github_match = re.search(GITHUB_REGEX, text, re.IGNORECASE)
    if github_match:
        parsed_data["github"] = github_match.group(0)
        
    # 2. Extract Name (Rule-based & spaCy NER)
    parsed_data["name"] = extract_name(text)
    
    # 3. Parse Sections
    parsed_data["sections"] = split_sections(text)
    
    # 4. Extract categorized skills (calls skill_extractor)
    parsed_data["skills"] = extract_skills(text)
    
    return parsed_data

def extract_name(text: str) -> str:
    """
    Extract candidate name from the top part of the resume.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return "Unknown"
        
    # Standard spaCy model check
    try:
        nlp = spacy.load("en_core_web_sm")
        # Process the first 3 lines together
        top_lines = " ".join(lines[:3])
        doc = nlp(top_lines)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Ensure it's not a False Positive (e.g. email components or common tags)
                name = ent.text.strip()
                # A name should typically be between 2 and 4 words and contain only letters
                if len(name.split()) >= 2 and len(name.split()) <= 4 and re.match(r"^[a-zA-Z\s]+$", name):
                    return name
    except Exception:
        pass
        
    # Fallback heuristic: check top 3 lines
    for line in lines[:3]:
        # Exclude contact info lines
        if "@" in line or any(p in line.lower() for p in ["resume", "curriculum", "cv", "portfolio", "http", "phone"]):
            continue
        words = line.split()
        if len(words) >= 2 and len(words) <= 4 and re.match(r"^[a-zA-Z\s]+$", line):
            return line
            
    return "Unknown"

def split_sections(text: str) -> dict:
    """
    Splits the resume text into standard sections based on keywords.
    """
    sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "certifications": "",
        "skills_raw": ""
    }
    
    lines = text.split("\n")
    current_section = None
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        # Detect if the line is a section header
        detected_section = None
        # Headers are usually short, e.g., less than 30 characters
        if len(line_clean) < 30:
            line_lower = line_clean.lower().strip(":-*# ")
            for sec, synonyms in SECTION_HEADERS.items():
                if line_lower in synonyms:
                    detected_section = sec
                    break
                    
        # Update current section pointer
        if detected_section:
            current_section = detected_section
            continue
            
        # If we have a current section, append line to it
        if current_section:
            # Map internal keys
            key = "skills_raw" if current_section == "skills" else current_section
            sections[key] += line + "\n"
            
    # Clean up results
    for key in sections:
        sections[key] = sections[key].strip()
        
    return sections
