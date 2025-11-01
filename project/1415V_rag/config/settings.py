from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "..", "rag_faiss_index")
OPEN_API_KEY = os.getenv("OPEN_API_KEY")