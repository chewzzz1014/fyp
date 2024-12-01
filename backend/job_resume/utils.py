import json

def calculate_job_resume_score(resume_ner_prediction: str, job_ner_prediction: str) -> float:
    # Parse predictions
    resume_entities = json.loads(resume_ner_prediction) if resume_ner_prediction else []
    job_entities = json.loads(job_ner_prediction) if job_ner_prediction else []

    # Extract relevant entities (e.g., skills, company names)
    resume_skills = {ent['text'] for ent in resume_entities if ent['label'] == 'SKILL'}
    job_skills = {ent['text'] for ent in job_entities if ent['label'] == 'SKILL'}

    # Calculate similarity (intersection over union)
    if not resume_skills or not job_skills:
        return 0.0

    intersection = resume_skills.intersection(job_skills)
    union = resume_skills.union(job_skills)

    return len(intersection) / len(union)
