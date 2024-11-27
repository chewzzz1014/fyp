import spacy
import string
from backend.core.config import NER_MODEL_PATH

def preprocess_input_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

def load_trained_mode():
    try:
        nlp = spacy.load(NER_MODEL_PATH)
        return nlp
    except Exception as e:
        raise RuntimeError(f"Failed to load SpaCy model: {e}")