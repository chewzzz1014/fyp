from typing import List, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import string

def normalize_skills(skills: Set[str]) -> List[str]:
    """
    Normalize skills by:
    - Converting to lowercase
    - Removing punctuation
    - Stripping whitespace
    - Removing duplicate skills
    
    Args:
        skills (Set[str]): Set of skills to normalize
    
    Returns:
        List[str]: Normalized list of unique skills
    """
    # Remove punctuation and convert to lowercase
    translator = str.maketrans('', '', string.punctuation)
    normalized = {
        skill.lower().translate(translator).strip() 
        for skill in skills
    }
    
    # Remove empty strings and duplicates
    return list(filter(bool, normalized))

def compute_tfidf_similarity(skills1: List[str], skills2: List[str]) -> float:
    """
    Compute TF-IDF based cosine similarity between two skill sets.
    
    Args:
        skills1 (List[str]): First set of skills
        skills2 (List[str]): Second set of skills
    
    Returns:
        float: Cosine similarity score
    """
    if not skills1 or not skills2:
        return 0.0
    
    # Combine skills into documents
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([' '.join(skills1), ' '.join(skills2)])
    
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

def compute_string_similarity(skills1: List[str], skills2: List[str]) -> float:
    """
    Compute string-based similarity using difflib.
    
    Args:
        skills1 (List[str]): First set of skills
        skills2 (List[str]): Second set of skills
    
    Returns:
        float: Average string similarity score
    """
    if not skills1 or not skills2:
        return 0.0
    
    # Compute pairwise similarities
    similarities = []
    for skill1 in skills1:
        for skill2 in skills2:
            # Use SequenceMatcher for string similarity
            similarity = difflib.SequenceMatcher(None, skill1, skill2).ratio()
            similarities.append(similarity)
    
    return sum(similarities) / len(similarities) if similarities else 0.0

def compute_jaccard_similarity(skills1: List[str], skills2: List[str]) -> float:
    """
    Compute Jaccard similarity between two skill sets.
    
    Args:
        skills1 (List[str]): First set of skills
        skills2 (List[str]): Second set of skills
    
    Returns:
        float: Jaccard similarity score
    """
    set1 = set(skills1)
    set2 = set(skills2)
    
    # Compute Jaccard similarity
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0