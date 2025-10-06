from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일(config/settings.py)의 절대경로
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "..", "rag_faiss_index")  # hybrid_rag/rag_faiss_index
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")