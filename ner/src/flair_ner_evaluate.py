# python flair_ner_evaluate.py

from flair.data import Corpus
from flair.datasets import ColumnCorpus
from flair.models import SequenceTagger

# flair_ner/
# ├── flair_ner_train.py (*)
# ├── flair_train.txt
# ├── flair_test.txt
# ├── flair_output/
# │   ├── final-model.pt
# │   ├── loss.tsv
# │   └── training.log
# ├── flair_train_log.txt
# └── flair_evaluation_results.txt (NEW)

# File paths
MODEL_PATH = './flair_output/final-model.pt'
DATA_FOLDER = './'
TRAIN_FILE = 'flair_train.txt'
TEST_FILE = 'flair_test.txt'
OUTPUT_FILE = './flair_evaluation_results.txt'

# Define columns for CoNLL format
COLUMNS = {0: 'text', 1: 'ner'}

def evaluate_flair_model(model_path: str, data_folder: str, train_file: str, test_file: str, output_file: str):
    """
    Load a trained Flair NER model, evaluate it on the test dataset, and save the results to a file.
    
    Args:
        model_path (str): Path to the trained Flair model file.
        data_folder (str): Path to the data folder containing train/test files.
        train_file (str): Name of the train file.
        test_file (str): Name of the test file.
        output_file (str): Path to save evaluation results.
    """
    # Load the corpus
    corpus: Corpus = ColumnCorpus(
        data_folder,
        COLUMNS,
        train_file=train_file,
        test_file=test_file,
        dev_file=None
    )

    # Load the trained model
    tagger = SequenceTagger.load(model_path)
    print(f"Loaded model from {model_path}")

    # Evaluate the model on the test dataset
    print("Evaluating the model on the test dataset...")
    result = tagger.evaluate(corpus.test, gold_label_type='ner', mini_batch_size=32)


    # Print results to CLI
    print("\n" + result)

    # Save results to a text file
    with open(output_file, 'w') as f:
        f.write(str(result))
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    # Run the evaluation
    evaluate_flair_model(MODEL_PATH, DATA_FOLDER, TRAIN_FILE, TEST_FILE, OUTPUT_FILE)
