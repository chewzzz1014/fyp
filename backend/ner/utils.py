import spacy
from backend.core.config import NER_MODEL_PATH
import re

def remove_non_alphanumeric(text):
    if text is None:
        return ''
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)
def load_trained_mode():
    try:
        nlp = spacy.load(NER_MODEL_PATH)
        return nlp
    except Exception as e:
        raise RuntimeError(f"Failed to load SpaCy model: {e}")
    
def make_prediction(text):
    nlp = load_trained_mode()
    doc = nlp(text)
    entities = [
        {"text": ent.text, "start": ent.start_char, "end": ent.end_char, "label": ent.label_}
        for ent in doc.ents
    ]
    return entities