import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'truthlens-ai-super-secret-key-2026-secure-key'
    DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
    DATASET_PATH = os.path.join(BASE_DIR, 'dataset', 'news.csv')
    MODEL_DIR = os.path.join(BASE_DIR, 'model')
    MODEL_PATH = os.path.join(MODEL_DIR, 'fake_news_model.pkl')
    VECTORIZER_PATH = os.path.join(MODEL_DIR, 'tfidf_vectorizer.pkl')
    METRICS_PATH = os.path.join(MODEL_DIR, 'metrics.json')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max payload
