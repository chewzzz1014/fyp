from fastapi import APIRouter, HTTPException
from .schema import NERRequest, NERResponse
from .utils import load_trained_mode, preprocess_input_text

router = APIRouter()

@router.post("/predict", response_model=NERResponse)
def predict(request: NERRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    nlp = load_trained_mode()

    # doc = nlp(preprocess_input_text(request.text))
    doc = nlp(request.text)
    entities = [
        {"text": ent.text, "start": ent.start_char, "end": ent.end_char, "label": ent.label_}
        for ent in doc.ents
    ]
    return {"entities": entities}