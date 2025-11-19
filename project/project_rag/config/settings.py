from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR_PATH = [
    os.path.join(BASE_DIR, "..", "..", "..", "project_txt", "1415V"),
    os.path.join(BASE_DIR, "..", "..", "..", "project_txt", "1415S")
]
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "..", "rag_faiss_index")
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")