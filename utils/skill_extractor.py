import re
import spacy
import logging

logger = logging.getLogger(__name__)

# Predefined dictionary of skills categorized by type
SKILLS_DB = {
    "Programming Languages": [
        "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript", "Ruby", "Go", "Golang", "Rust", 
        "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Shell", "Bash", "PowerShell", "COBOL", 
        "Fortran", "Haskell", "SQL", "HTML", "CSS", "Solidity", "Dart"
    ],
    "Frameworks & Libraries": [
        "React", "Angular", "Vue", "Django", "Flask", "FastAPI", "Spring Boot", "Spring", "Express", 
        "Rails", "Ruby on Rails", "ASP.NET", "Laravel", "Next.js", "Nuxt.js", "Svelte", "Tailwind CSS", "Tailwind", 
        "Bootstrap", "jQuery", "TensorFlow", "PyTorch", "Keras", "Scikit-Learn", "Sklearn", "Spark", 
        "Hadoop", "Pandas", "NumPy", "Matplotlib", "Seaborn", "OpenCV", "NLTK", "spaCy", "Hugging Face", "Huggingface", 
        "Hibernate", "Node.js", "Nodejs", "React Native", "Flutter", "Ionic", "Redux", "GraphQL"
    ],
    "Databases": [
        "PostgreSQL", "Postgres", "MySQL", "SQLite", "MongoDB", "Redis", "Oracle", "SQL Server", 
        "Cassandra", "Firebase", "DynamoDB", "Neo4j", "MariaDB", "Elasticsearch", "InfluxDB"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Heroku", "DigitalOcean", 
        "Vercel", "Netlify", "Cloudflare", "Docker", "Kubernetes", "K8s", "Jenkins", "Ansible", 
        "Terraform", "Puppet", "Chef", "CI/CD", "CircleCI", "GitHub Actions", "GitLab CI", 
        "Prometheus", "Grafana", "Nginx", "Apache", "Docker Swarm"
    ],
    "Tools & Platforms": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Trello", "Postman", "Figma", 
        "Canva", "Excel", "Power BI", "PowerBI", "Tableau", "VS Code", "VSCode", "IntelliJ", 
        "Eclipse", "PyCharm", "Jupyter", "Slack", "Salesforce", "SAP", "WordPress", "Shopify"
    ],
    "Soft Skills": [
        "Communication", "Leadership", "Teamwork", "Collaboration", "Problem Solving", 
        "Time Management", "Adaptability", "Critical Thinking", "Creativity", 
        "Conflict Resolution", "Negotiation", "Project Management", "Agile", 
        "Scrum", "Active Listening", "Decision Making", "Presentation", "Public Speaking", 
        "Emotional Intelligence", "Work Ethic", "Interpersonal Skills", "Interpersonal"
    ]
}

# Load spaCy model for NLP. Download if not available.
nlp = None
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # We will try downloading it programmatically inside app.py or fallback gracefully
    pass

def extract_skills(text: str) -> dict:
    """
    Extracts skills from text, categorized by Programming Languages, Frameworks,
    Databases, Cloud Platforms, Tools, and Soft Skills.
    
    Args:
        text (str): Resume raw text.
        
    Returns:
        dict: A dictionary containing categorized list of skills extracted.
    """
    global nlp
    extracted = {category: set() for category in SKILLS_DB.keys()}
    
    # Pre-process text: clean spacing but preserve capitalization for POS analysis
    cleaned_text = re.sub(r'\s+', ' ', text)
    
    # Process text using spaCy if available
    doc = None
    if nlp is not None:
        try:
            doc = nlp(cleaned_text)
        except Exception as e:
            logger.warning(f"spaCy processing failed: {str(e)}")
            
    # For spaCy token checking (mainly to check part of speech for tricky words)
    pos_dict = {}
    if doc:
        for token in doc:
            token_text = token.text.lower()
            pos_dict[token_text] = token.pos_
            
    # Compile regexes or check occurrences
    for category, skill_list in SKILLS_DB.items():
        for skill in skill_list:
            # Handle special characters in regex
            skill_escaped = re.escape(skill)
            
            # Words with special characters at the end (like C++, C#) need custom word boundaries
            if skill.endswith("++") or skill.endswith("#"):
                pattern = rf"\b{skill_escaped}(?!\w)"
            else:
                pattern = rf"\b{skill_escaped}\b"
                
            # Perform case-insensitive search
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
            
            if matches:
                # Special validation for "Go" (avoid matching verb "go" or "ongoing")
                if skill.lower() == "go":
                    # Check if capitalized in text, or if spaCy says it is a proper noun (PROPN) or noun (NOUN)
                    # We look for "Go" exactly, or "golang"
                    has_golang = re.search(r"\bgolang\b", cleaned_text, re.IGNORECASE)
                    has_proper_go = re.search(r"\bGo\b", cleaned_text) # Case sensitive
                    
                    # Verify POS if spaCy is active
                    is_verb = pos_dict.get("go") == "VERB"
                    
                    if has_golang or (has_proper_go and not is_verb):
                        extracted[category].add("Go")
                # Special validation for "C" (avoid single character matching in sentences)
                elif skill.lower() == "c":
                    # Look for capitalized 'C' with surrounding spacing or punctuation, like "C, Unix" or "C and C++"
                    has_c_lang = re.search(r"\bC\b", cleaned_text) # Case sensitive
                    if has_c_lang:
                        # Make sure it's not a grade or middle initial like "John C. Doe" or "Section C"
                        # Simple check: verify it's near tech keywords or in a technical list
                        context_words = ["programming", "language", "unix", "linux", "developer", "c++", "c#", "java", "python", "software", "embedded"]
                        text_lower = cleaned_text.lower()
                        is_likely_lang = any(word in text_lower for word in context_words)
                        if is_likely_lang:
                            extracted[category].add("C")
                # Special validation for "R"
                elif skill.lower() == "r":
                    has_r_lang = re.search(r"\bR\b", cleaned_text) # Case sensitive
                    if has_r_lang:
                        context_words = ["statistics", "data science", "r programming", "analysis", "ggplot", "rstudio", "python", "sas", "spss"]
                        text_lower = cleaned_text.lower()
                        is_likely_lang = any(word in text_lower for word in context_words)
                        if is_likely_lang:
                            extracted[category].add("R")
                else:
                    # Regular matching: add the normalized spelling from SKILLS_DB
                    extracted[category].add(skill)
                    
    # Convert sets to sorted lists
    return {category: sorted(list(skills)) for category, skills in extracted.items()}
