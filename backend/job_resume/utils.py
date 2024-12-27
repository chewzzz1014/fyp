import json
from .calc_score.cosine_similarity import normalize_skills, compute_tfidf_similarity, sigmoid

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
    
    # If either skill set is empty, return 0
    if not resume_skills or not job_skills:
        return 0.0
    
    # Normalize skills
    normalized_resume_skills = normalize_skills(resume_skills)
    normalized_job_skills = normalize_skills(job_skills)
    
    # TF-IDF Cosine Similarity
    tfidf_similarity = compute_tfidf_similarity(normalized_resume_skills, normalized_job_skills)
    
    # Normalize similairy score
    final_similarity_score = sigmoid(tfidf_similarity, scale=20, shift=3)
    
    return final_similarity_score