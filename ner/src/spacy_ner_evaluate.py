


# RUN THIS COMMAND AFTER MODEL IS TRAINED IN spacy_ner/
# python -m spacy evaluate spacy_output/model-best spacy_ner_data/test_data.spacy --gpu-id 0 -dp spacy_output | tee spacy_evaluation_results.txt


# spacy_ner/
# ├── spacy_ner_train.py (*)
# ├── config.cfg (*)
# ├── spacy_ner_data/
# │   ├── train_data.spacy
# │   └── test_data.spacy
# ├── spacy_output/
# │   ├── best-model/
# │   └── last-model/
# ├── spacy_train_log.txt
# └── spacy_evaluation_results.txt (NEW)