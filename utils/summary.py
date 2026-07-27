import re
import logging

logger = logging.getLogger(__name__)

# Keywords that indicate summary value or achievements
SUMMARY_KEYWORDS = [
    "experience", "years", "led", "managed", "developed", "architected", "designed", 
    "responsible", "skills", "expert", "specialist", "proven track record", "successful", 
    "achieved", "delivered", "solved", "created", "engineered", "implemented", "spearheaded"
]

def generate_summary(raw_text: str, extracted_skills: dict) -> str:
    """
    Generates a concise professional summary using extractive NLP text summarization.
    
    Args:
        raw_text (str): Resume raw text.
        extracted_skills (dict): Extracted skills from skill_extractor.
        
    Returns:
        str: Summarized text.
    """
    if not raw_text or not raw_text.strip():
        return "No resume content provided to generate a summary."
        
    # Clean the text
    cleaned_text = re.sub(r'\s+', ' ', raw_text)
    
    # Simple sentence tokenizer
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15] # filter short lines
    
    if not sentences:
        return "Resume lacks complete sentences to extract a summary."
        
    # Collect all skills in a lowercase set for matching
    skills_set = set()
    for cat_skills in extracted_skills.values():
        for s in cat_skills:
            skills_set.add(s.lower())
            
    sentence_scores = {}
    
    for idx, sentence in enumerate(sentences):
        score = 0
        sent_lower = sentence.lower()
        words = sent_lower.split()
        word_count = len(words)
        
        # Sentence length penalty/reward (ideal length: 12-25 words)
        if 12 <= word_count <= 25:
            score += 3
        elif 6 <= word_count < 12:
            score += 1
        elif word_count > 30:
            score -= 2 # too long, usually a messy bullet list
            
        # Match achievements/experience keywords
        for keyword in SUMMARY_KEYWORDS:
            if keyword in sent_lower:
                score += 2
                
        # Match skills keywords
        for skill in skills_set:
            # Escape to prevent regex breaks
            try:
                if re.search(rf"\b{re.escape(skill)}\b", sent_lower):
                    score += 1.5
            except Exception:
                if skill in sent_lower:
                    score += 1
                    
        # Give higher weight to earlier sentences (which are usually profile summaries or core experience)
        if idx < 5:
            score += 3
        elif idx < 10:
            score += 1.5
            
        sentence_scores[idx] = score
        
    # Select top 3 or 4 sentences
    top_sentences_indices = sorted(sentence_scores.keys(), key=lambda k: sentence_scores[k], reverse=True)[:3]
    
    # Sort indices so the summary sentences appear in the order of the original text
    top_sentences_indices.sort()
    
    extracted_summary_sentences = [sentences[idx] for idx in top_sentences_indices]
    
    summary = " ".join(extracted_summary_sentences)
    
    # If the summary is extremely short or empty, fallback
    if len(summary) < 50:
        # Fallback to the first few lines of the experience or the top of the resume
        summary = " ".join(sentences[:2])
        
    return summary
