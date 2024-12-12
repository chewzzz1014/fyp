import re
import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

# text cleaning: remove non-alphabetic characters and extra spaces
def clean_text(text):
    if pd.isna(text) or text is None:
        return ""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

# tokenization
def tokenize(text):
    return word_tokenize(text)

# stop word removal
def tokenize_text(text):
    return [word for word in tokenize(text) if word not in stop_words]

# stemming
def stem_text(tokens):
    return [stemmer.stem(word) for word in tokens]

# lemmatization
def lemmatize_text(tokens, nlp):
    # doc = nlp(" ".join(tokens))
    # return [token.lemma_ for token in doc]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

def preprocess_text(text, nlp):
    text = clean_text(text)
    tokens = tokenize_text(text)
    lemmatized_tokens = lemmatize_text(tokens, nlp)
    # return lemmatized_tokens
    return ' '.join(lemmatized_tokens)