from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

pretrained_model = spacy.load("en_core_web_lg")

def compute_similarity_skill(skills1, skills2):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([' '.join(skills1), ' '.join(skills2)])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

def compute_semantic_similarity(skills1, skills2):
    if not skills1 or not skills2:
        return 0.0
    skill_vectors1 = [pretrained_model(skill).vector for skill in skills1]
    skill_vectors2 = [pretrained_model(skill).vector for skill in skills2]
    similarity_matrix = cosine_similarity(skill_vectors1, skill_vectors2)
    return similarity_matrix.mean()

def normalize_skills(skills):
    # avoid redundant skill
    return set([skill.lower().strip() for skill in skills])