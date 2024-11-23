from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
from pathlib import Path
import string

# Load the trained SpaCy NER model
MODEL_PATH = Path(__file__).resolve().parent.parent / "ner-trained-models" / "spacy_output" / "model-best"

try:
    nlp = spacy.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"Failed to load SpaCy model: {e}")

app = FastAPI()

# Define input schema
class NERRequest(BaseModel):
    text: str

# Define output schema (optional, for structured response)
class NERResponse(BaseModel):
    entities: list

@app.get("/")
def home():
    return {"message": "Welcome to the NER model API. Use /predict to analyze text."}

def preprocess_input_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

@app.post("/predict", response_model=NERResponse)
def predict(request: NERRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    # doc = nlp(preprocess_input_text(request.text))
    doc = nlp(request.text)
    entities = [
        {"text": ent.text, "start": ent.start_char, "end": ent.end_char, "label": ent.label_}
        for ent in doc.ents
    ]
    return {"entities": entities}
