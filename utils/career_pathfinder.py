import logging

logger = logging.getLogger(__name__)

# Standard career roles and their key skills requirements
CAREER_ROLES = {
    "Backend Developer": [
        "Python", "Django", "Flask", "FastAPI", "Java", "Spring Boot", "SQL", "PostgreSQL", 
        "MySQL", "MongoDB", "Redis", "Docker", "AWS", "CI/CD", "Git"
    ],
    "Frontend Developer": [
        "JavaScript", "TypeScript", "React", "Angular", "Vue", "HTML", "CSS", "Tailwind CSS", 
        "Bootstrap", "Figma", "Git", "Redux", "GraphQL"
    ],
    "Full Stack Developer": [
        "React", "Node.js", "Express", "JavaScript", "TypeScript", "Python", "SQL", "PostgreSQL", 
        "MongoDB", "Docker", "Git", "HTML", "CSS", "CI/CD"
    ],
    "Data Scientist & AI Engineer": [
        "Python", "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "SQL", "R", 
        "Matplotlib", "Seaborn", "Jupyter"
    ],
    "DevOps & Cloud Engineer": [
        "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", "Ansible", "Terraform", 
        "CI/CD", "Linux", "Bash", "Shell", "Git", "Prometheus", "Grafana"
    ],
    "Data Analyst": [
        "SQL", "Excel", "Python", "Pandas", "Tableau", "Power BI", "Git"
    ]
}

def analyze_career_suitability(extracted_skills: dict) -> dict:
    """
    Compares extracted resume skills against standard career profiles.
    
    Args:
        extracted_skills (dict): Categorized extracted skills.
        
    Returns:
        dict: Roles matched, suitability scores, and skills roadmap.
    """
    # Flatten extracted skills to a single set of lowercase terms for matching
    resume_skills_lower = set()
    resume_skills_display = {} # mapping of lowercase -> original display spelling
    
    for category, skill_list in extracted_skills.items():
        for skill in skill_list:
            lower_skill = skill.lower()
            resume_skills_lower.add(lower_skill)
            resume_skills_display[lower_skill] = skill
            
    analysis_results = {}
    
    for role_name, required_skills in CAREER_ROLES.items():
        # Match
        matched = []
        missing = []
        
        for req in required_skills:
            req_lower = req.lower()
            if req_lower in resume_skills_lower:
                matched.append(resume_skills_display[req_lower])
            else:
                missing.append(req)
                
        # Calculate suitability score out of 100
        score = 0
        if required_skills:
            score = int((len(matched) / len(required_skills)) * 100)
            
        analysis_results[role_name] = {
            "suitability_score": score,
            "matched_skills": matched,
            "missing_skills": missing
        }
        
    # Sort roles by suitability score descending
    sorted_roles = sorted(
        analysis_results.items(), 
        key=lambda x: x[1]["suitability_score"], 
        reverse=True
    )
    
    return {
        "roles_ranking": sorted_roles,
        "raw_analysis": analysis_results
    }
