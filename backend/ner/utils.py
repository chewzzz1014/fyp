import spacy
from backend.core.config import BUCKET_NAME, MODEL_FOLDER, LOCAL_MODEL_PATH
import re
import os
from google.cloud import storage

storage_client = storage.Client()

def remove_non_alphanumeric(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def download_model_from_gcs():
    """
    Download all files from the model folder in GCS to the local directory.
    """
    bucket = storage_client.get_bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=MODEL_FOLDER)

    # Ensure the local directory exists
    os.makedirs(LOCAL_MODEL_PATH, exist_ok=True)

    for blob in blobs:
        # Extract the relative path and save the file locally
        local_path = os.path.join(LOCAL_MODEL_PATH, os.path.relpath(blob.name, MODEL_FOLDER))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
        print(f"Downloaded {blob.name} to {local_path}")
    
def make_prediction(text):
    nlp = spacy.load(LOCAL_MODEL_PATH)

    doc = nlp(text)
    entities = [
        {"text": ent.text, "start": ent.start_char, "end": ent.end_char, "label": ent.label_}
        for ent in doc.ents
    ]
    return entities