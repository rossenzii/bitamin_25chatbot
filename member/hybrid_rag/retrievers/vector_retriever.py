import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 상대 import를 절대 import로 변경
try:
    from member.hybrid_rag.config.settings import OPENAI_API_KEY, FAISS_INDEX_PATH
except ImportError:
    # 상대 import fallback (로컬 실행 시)
    from config.settings import OPENAI_API_KEY, FAISS_INDEX_PATH

def get_vector_retriever():
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.load_local(
        FAISS_INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    # mmr: 질문과 유사하면서 서로 다른 문서 반환 k: 최종 반환 문서, fetch_k: 후보 문서 수, lambda_mult: 유사도 가중치
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 10, "fetch_k": 30, "lambda_mult": 0.7}  # k값 축소로 속도 개선
    )
    return retriever, vectorstore