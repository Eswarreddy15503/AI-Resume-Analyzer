import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skill_extractor import extract_skills
import logging

logger = logging.getLogger(__name__)

# List of English stop words to exclude during keyword analysis (simple fallback if nltk is not downloaded)
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "arent", "as", "at", 
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "cant", "cannot", "could", 
    "couldnt", "did", "didnt", "do", "does", "doesnt", "doing", "dont", "down", "during", "each", "few", "for", "from", 
    "further", "had", "hadnt", "has", "hasnt", "have", "havent", "having", "he", "hed", "hell", "hes", "her", "here", 
    "heres", "hers", "herself", "him", "himself", "his", "how", "hows", "i", "id", "ill", "im", "ive", "if", "in", "into", 
    "is", "isnt", "it", "its", "itself", "lets", "me", "more", "most", "mustnt", "my", "myself", "no", "nor", "not", "of", 
    "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shant", 
    "she", "shed", "shell", "shes", "should", "shouldnt", "so", "some", "such", "than", "that", "thats", "the", "their", 
    "theirs", "them", "themselves", "then", "there", "theres", "these", "they", "theyd", "theyll", "theyre", "theyve", 
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasnt", "we", "wed", "well", "were", 
    "weve", "werent", "what", "whats", "when", "whens", "where", "wheres", "which", "while", "who", "whos", "whom", 
    "why", "whys", "with", "wont", "would", "wouldnt", "you", "youd", "youll", "youre", "youve", "your", "yours", 
    "yourself", "yourselves", "requirements", "responsibilities", "role", "description", "job", "candidate", "position", 
    "work", "experience", "skills", "ability", "duties", "qualifications", "required"
}

def match_job_description(resume_text: str, jd_text: str) -> dict:
    """
    Compares resume text to a job description.
    
    Args:
        resume_text (str): Extracted resume text.
        jd_text (str): Job description text.
        
    Returns:
        dict: Match stats including Match %, Matched Skills, Missing Skills, and Keyword Frequencies.
    """
    result = {
        "match_percentage": 0,
        "matched_skills": [],
        "missing_skills": [],
        "keyword_analysis": [] # list of dicts: {"keyword": x, "jd_count": y, "resume_count": z}
    }
    
    if not resume_text.strip() or not jd_text.strip():
        return result
        
    # 1. Skill Extraction from JD and Resume
    resume_skills_dict = extract_skills(resume_text)
    jd_skills_dict = extract_skills(jd_text)
    
    # Flatten skills into lists
    resume_skills = set()
    for cat_skills in resume_skills_dict.values():
        resume_skills.update(cat_skills)
        
    jd_skills = set()
    for cat_skills in jd_skills_dict.values():
        jd_skills.update(cat_skills)
        
    # Find matching and missing skills
    matched_skills = sorted(list(resume_skills.intersection(jd_skills)))
    missing_skills = sorted(list(jd_skills.difference(resume_skills)))
    
    result["matched_skills"] = matched_skills
    result["missing_skills"] = missing_skills
    
    # 2. Text Cosine Similarity using TF-IDF
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    except Exception as e:
        logger.error(f"Cosine similarity calculation failed: {str(e)}")
        sim = 0.0
        
    # 3. Calculate Overall Match %
    # Match percentage is a combination of text similarity (40%) and skill coverage (60%)
    skill_match_ratio = 1.0
    if len(jd_skills) > 0:
        skill_match_ratio = len(matched_skills) / len(jd_skills)
        
    # Adjust weights: skill coverage is highly important for recruiters
    match_percentage = (sim * 40) + (skill_match_ratio * 60)
    # Clip and convert to integer
    result["match_percentage"] = int(np.clip(match_percentage, 0, 100))
    
    # 4. Keyword Analysis (Frequent nouns / phrases in JD vs Resume)
    result["keyword_analysis"] = extract_keywords_comparison(resume_text, jd_text)
    
    return result

def extract_keywords_comparison(resume_text: str, jd_text: str) -> list:
    """
    Extracts top keywords from JD and counts their occurrences in both JD and Resume.
    """
    comparison = []
    
    # Clean and split words
    jd_words = re.findall(r"\b[a-zA-Z]{3,20}\b", jd_text.lower())
    resume_words = re.findall(r"\b[a-zA-Z]{3,20}\b", resume_text.lower())
    
    # Count frequencies in JD
    jd_freq = {}
    for word in jd_words:
        if word not in STOP_WORDS:
            jd_freq[word] = jd_freq.get(word, 0) + 1
            
    # Count frequencies in Resume
    resume_freq = {}
    for word in resume_words:
        resume_freq[word] = resume_freq.get(word, 0) + 1
        
    # Get top 15 words in JD
    top_jd_keywords = sorted(jd_freq.items(), key=lambda item: item[1], reverse=True)[:15]
    
    for word, count in top_jd_keywords:
        comparison.append({
            "keyword": word.capitalize(),
            "jd_count": count,
            "resume_count": resume_freq.get(word, 0)
        })
        
    return comparison
