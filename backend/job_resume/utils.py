import json
from .calc_score.cosine_similarity import normalize_skills, compute_similarity_skill, compute_semantic_similarity

def calculate_job_resume_score(
    resume_ner_prediction: str,
    job_ner_prediction: str
) -> float:
    # Parse predictions
    resume_entities = json.loads(resume_ner_prediction) if resume_ner_prediction else []
    job_entities = json.loads(job_ner_prediction) if job_ner_prediction else []

    # Extract SKILL entities
    resume_skills = {ent['text'] for ent in resume_entities if ent['label'] == 'SKILL'}
    job_skills = {ent['text'] for ent in job_entities if ent['label'] == 'SKILL'}

    # If either skill is empty
    if not resume_skills or not job_skills:
        return 0.0

    # Transform list into text
    normalized_resume_skills = normalize_skills(resume_skills)
    normalized_job_skills = normalize_skills(job_skills)
    
    # Calculate similarity
    # 1. between skills extracted from text
    skill_similarity_score = compute_similarity_skill(normalized_resume_skills, normalized_job_skills)
    # 2. between skills extracted from text, semantical comparision
    semantic_skill_similarity_score = compute_semantic_similarity(normalized_resume_skills, normalized_job_skills)

    final_similarity_score = 0.7 * skill_similarity_score + 0.3 * semantic_skill_similarity_score
    
    return final_similarity_score