# python spacy_ner_train.py > train_log.txt

import json
import os
import random
from sklearn.model_selection import train_test_split
import spacy
from spacy.tokens import DocBin
from spacy.lang.en import English
import numpy as np
import subprocess

# Ensure numpy compatibility
np.float_ = np.float64

# File structure: 
# ner_datasets/
# └── 1100_resumes_annotated.json

# spacy_ner/
# ├── spacy_ner_train.py
# ├── spacy_ner_data/
# │   ├── train_data.spacy
# │   └── test_data.spacy
# ├── spacy_output/
# │   ├── best-model/
# │   └── last-model/
# ├── config.cfg
# └── train_log.txt
JSON_PATH = "../ner_datasets/1100_resumes_annotated.json"  # Update with the actual path to your JSON file
SPACY_DATA_PATH = "spacy_ner_data"  # Directory to save .spacy files
OUTPUT_PATH = "./spacy_output"  # Directory to save the trained model
CONFIG_PATH = "./config.cfg"  # Path to SpaCy config file
LOG_PATH = "./train_log.txt"  # Path to save training logs

# Ensure output directories exist
os.makedirs(SPACY_DATA_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)

# pip install git+https://github.com/explosion/spacy-transformers
# pip install -U spacy
# pip install "numpy<2"
# python -m spacy download en_core_web_lg
def install_dependencies():
    subprocess.check_call(["pip", "install", "-U", "spacy", "numpy<2"])
    subprocess.check_call(["pip", "install", "git+https://github.com/explosion/spacy-transformers"])
    subprocess.check_call(["python", "-m", "spacy", "download", "en_core_web_lg"])

# Remove overlapping entities
def remove_overlapping_entities(entities):
    entities = sorted(entities, key=lambda x: x[0])
    non_overlapping = []
    last_end = -1
    for start, end, label in entities:
        if start >= last_end:
            non_overlapping.append((start, end, label))
            last_end = end
    return non_overlapping

# Convert JSON data to SpaCy's DocBin format
def convert_to_spacy_format(data):
    nlp = spacy.blank("en")
    doc_bin = DocBin()

    for item in data:
        text = item['data']['Text']
        entities = []

        for annotation in item['annotations'][0]['result']:
            start = annotation['value']['start']
            end = annotation['value']['end']
            label = annotation['value']['labels'][0]
            entities.append((start, end, label))

        entities = remove_overlapping_entities(entities)
        doc = nlp.make_doc(text)
        spans = [doc.char_span(start, end, label=label) for start, end, label in entities]
        spans = [span for span in spans if span is not None]
        doc.ents = spans
        doc_bin.add(doc)

    return doc_bin

# Count entity labels
def count_entity_labels(file_path):
    doc_bin = DocBin().from_disk(file_path)
    label_counts = {}
    for doc in doc_bin.get_docs(English().vocab):
        for ent in doc.ents:
            label = ent.label_
            label_counts[label] = label_counts.get(label, 0) + 1
    return label_counts

# Main function
def main():
    # Install dependencies
    install_dependencies()

    # Load JSON data
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    # Split data into train and test sets
    train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

    # Convert train and test sets to SpaCy format
    train_doc_bin = convert_to_spacy_format(train_data)
    test_doc_bin = convert_to_spacy_format(test_data)

    # Save the train and test data to .spacy files
    train_file = os.path.join(SPACY_DATA_PATH, "train_data.spacy")
    test_file = os.path.join(SPACY_DATA_PATH, "test_data.spacy")
    train_doc_bin.to_disk(train_file)
    test_doc_bin.to_disk(test_file)

    # Train the model and save output to a log file
    with open(LOG_PATH, "w") as log_file:
        train_command = [
            "python", "-m", "spacy", "train", CONFIG_PATH,
            "--output", OUTPUT_PATH, "--gpu-id", "0"
        ]
        subprocess.run(train_command, stdout=log_file, stderr=log_file)

    print(f"\nTraining complete. Model saved at: {OUTPUT_PATH}")
    print(f"Training logs saved at: {LOG_PATH}")

# Run script
if __name__ == "__main__":
    main()