import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError(f"DATABASE_URL is not set in the environment variables or .env file. {env_path}")

NER_MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "ner-trained-models" / "spacy_output" / "model-best"