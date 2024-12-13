import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 3600))


# gcp bucket
BUCKET_NAME = os.getenv("MODEL_BUCKET_NAME")
MODEL_FOLDER = os.getenv("MODEL_FOLDER")
LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH")