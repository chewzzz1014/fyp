# python flair_ner_train.py > train_log.txt

import subprocess
# pip install flair
def install_dependencies():
    subprocess.check_call(["pip", "install", "flair"])
install_dependencies()

import json
import random
from typing import List, Tuple
import spacy
from collections import defaultdict
from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.embeddings import WordEmbeddings, StackedEmbeddings, FlairEmbeddings
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer

# File structure: 
# ner_datasets/
# └── 1100_resumes_annotated.json

# flair_ner/
# ├── flair_ner_train.py
# ├── flair_train.txt
# ├── flair_test.txt
# ├── flair_output/
# │   ├── final-model.pt
# │   ├── loss.tsv
# │   └── training.log
# └── train_log.txt

JSON_PATH = "../ner_datasets/1100_resumes_annotated.json"
OUTPUT_PATH = './flair_output'
TRAINING_CONFIG = {
    'learning_rate': 0.05,
    'mini_batch_size': 16,
    'max_epochs': 50,
    'patience': 5,
    'use_amp': True,  # Mixed precision training
    'dropout': 0.2,  # Dropout for better capacity retention
    'rnn_layers': 2,  # Number of RNN layers
    'hidden_size': 128,  # Hidden size for the tagger
    'embedding_sources': [
        WordEmbeddings('glove'),  # GloVe word embeddings
        FlairEmbeddings('news-forward'),  # Forward Flair embeddings
        FlairEmbeddings('news-backward')  # Backward Flair embeddings
    ],
    'base_path': OUTPUT_PATH,  # Path to save the trained model
    'train_with_dev': True,
}

# Define the NERConverter class
class NERConverter:
    def __init__(self):
        # Load pretrained model from Spacy library to create Spacy Doc object
        self.nlp = spacy.load("en_core_web_sm")

    def get_bioes_label(self, token_index: int, entity_length: int, current_position: int, label: str) -> str:
        """
        Convert to BIOES format
        - S-: Single token entity
        - B-: Beginning of multi-token entity
        - I-: Inside of multi-token entity
        - E-: End of multi-token entity
        - O: Outside
        """
        if entity_length == 1:
            return f'S-{label}'
        if current_position == 0:
            return f'B-{label}'
        if current_position == entity_length - 1:
            return f'E-{label}'
        return f'I-{label}'

    def convert_to_bioes_format(self, json_data: List[dict]) -> List[List[Tuple[str, str]]]:
        """Convert JSON annotations to BIOES format."""
        all_sentences = []

        # Process all annotations in JSON file
        for item in json_data:
            text = item['data']['Text']
            doc = self.nlp(text)

            # Initialize character-level labels
            char_labels = ['O'] * len(text)

            # First pass: identify entity boundaries and lengths
            entity_spans = []
            if item['annotations'] and len(item['annotations']) > 0:
                for ann in item['annotations'][0]['result']:
                    if 'value' in ann:
                        start = ann['value']['start']
                        end = ann['value']['end']
                        label = ann['value']['labels'][0]
                        entity_spans.append((start, end, label))

            # Sort spans by start position
            entity_spans.sort(key=lambda x: x[0])

            # Second pass: apply BIOES labels
            for start, end, label in entity_spans:
                # Get tokens that are part of this entity
                entity_text = text[start:end]
                entity_doc = self.nlp(entity_text)
                entity_length = len([token for token in entity_doc if not token.is_space])

                # Set labels for the entire span
                current_token_idx = 0
                for i in range(start, end):
                    if i == start or text[i-1].isspace():
                        char_labels[i] = self.get_bioes_label(i, entity_length, current_token_idx, label)
                        current_token_idx += 1
                    else:
                        char_labels[i] = char_labels[i-1]

            # Convert to token-level labels
            current_sentence = []
            for sent in doc.sents:
                for token in sent:
                    # Get the most common label for the token's characters
                    token_chars_labels = char_labels[token.idx:token.idx + len(token.text)]
                    label_counts = defaultdict(int)
                    for char_label in token_chars_labels:
                        label_counts[char_label] += 1

                    token_label = max(label_counts.items(), key=lambda x: x[1])[0]
                    current_sentence.append((token.text, token_label))

                if current_sentence:
                    all_sentences.append(current_sentence)
                    current_sentence = []

        return all_sentences

    def write_flair_file(self, sentences: List[List[Tuple[str, str]]], filename: str):
        """Write sentences in BIOES format to file."""
        with open(filename, 'w', encoding='utf-8') as f:
            for sentence in sentences:
                for token, label in sentence:
                    f.write(f'{token} {label}\n')
                f.write('\n')

    def convert_and_split(self, json_data: List[dict], train_file: str, test_file: str, test_ratio: float = 0.2):
        """Convert JSON to BIOES format and split into train/test sets."""
        all_sentences = self.convert_to_bioes_format(json_data)

        # Shuffle and split based on test_ratio
        random.shuffle(all_sentences)
        split_idx = int(len(all_sentences) * (1 - test_ratio))

        # Use list slicing to split
        train_sentences = all_sentences[:split_idx]
        test_sentences = all_sentences[split_idx:]

        # Write to txt files
        self.write_flair_file(train_sentences, train_file)
        self.write_flair_file(test_sentences, test_file)

        return len(train_sentences), len(test_sentences)

def main():
    install_dependencies()

    # Load JSON data
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Initialize the converter class
    converter = NERConverter()

    # Convert JSON data into BIOES data and split into train and test
    train_count, test_count = converter.convert_and_split(
        json_data,
        train_file='flair_train.txt',
        test_file='flair_test.txt',
        test_ratio=0.2
    )
    print(f'Created {train_count} training sentences and {test_count} test sentences')

    # Define columns for CoNLL (0: word, 1: label)
    columns = {0: 'text', 1: 'ner'}

    # Set data folder and train and test paths
    data_folder = './'
    train_file = 'flair_train.txt'
    test_file = 'flair_test.txt'

    # Load the corpus
    corpus: Corpus = ColumnCorpus(data_folder, columns,
                                  train_file=train_file,
                                  test_file=test_file,
                                  dev_file=None)

    # Create NER tagger
    tag_dictionary = corpus.make_label_dictionary(label_type='ner')

    # 1. Using LSTM-CRF on top of frozen embeddings
    # Combine flair and glove embeddings
    embeddings = StackedEmbeddings(TRAINING_CONFIG['embedding_sources'])

    # 2. Configure tagger with memory and performance optimizations
    tagger = SequenceTagger(
        hidden_size=TRAINING_CONFIG['hidden_size'],  # Increased hidden size for more capacity
        embeddings=embeddings,
        tag_dictionary=tag_dictionary,
        tag_type='ner',
        use_crf=True,
        tag_format='BIOES',
        dropout=TRAINING_CONFIG['dropout'],  # Dropout for better capacity retention
        rnn_layers=TRAINING_CONFIG['rnn_layers'],  # Number of RNN layers
    )

    # Train Flair NER model
    trainer = ModelTrainer(tagger, corpus)

    trainer.train(
        base_path=TRAINING_CONFIG['base_path'],  # Path to save model
        learning_rate=TRAINING_CONFIG['learning_rate'],  # Learning rate for stable training
        mini_batch_size=TRAINING_CONFIG['mini_batch_size'],  # Mini batch size
        max_epochs=TRAINING_CONFIG['max_epochs'],  # Maximum epochs
        patience=TRAINING_CONFIG['patience'],  # Patience for early stopping
        train_with_dev=TRAINING_CONFIG['train_with_dev'],
        save_final_model=True,
        use_amp=TRAINING_CONFIG['use_amp'],  # Mixed precision training for faster training
    )

if __name__ == "__main__":
    main()