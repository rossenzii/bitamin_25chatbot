import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 환경 변수 우선 사용 (배포 환경 대응)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "rag_faiss_index")

# config import 시도 (선택사항)
if not OPENAI_API_KEY:
    try:
        from project.project_rag.config.settings import OPENAI_API_KEY as CONFIG_KEY, FAISS_INDEX_PATH as CONFIG_PATH
        OPENAI_API_KEY = CONFIG_KEY
        FAISS_INDEX_PATH = CONFIG_PATH
    except ImportError:
        try:
            from config.settings import OPENAI_API_KEY as CONFIG_KEY, FAISS_INDEX_PATH as CONFIG_PATH
            OPENAI_API_KEY = CONFIG_KEY
            FAISS_INDEX_PATH = CONFIG_PATH
        except ImportError:
            pass

def get_vector_retriever():
    from pathlib import Path
    
    # 인덱스 파일 존재 확인
    index_path = Path(FAISS_INDEX_PATH)
    faiss_file = index_path / "index.faiss"
    
    if not faiss_file.exists():
        raise FileNotFoundError(
            f"FAISS 인덱스를 찾을 수 없습니다: {FAISS_INDEX_PATH}\n"
            f"먼저 'python project/project_rag/build_index.py'를 실행하여 인덱스를 생성하세요."
        )

    embeddings=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    try:
        vectorstore=FAISS.load_local(
            folder_path=FAISS_INDEX_PATH,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        # allow_dangerous_deserialization가 지원되지 않는 경우
        vectorstore=FAISS.load_local(
            folder_path=FAISS_INDEX_PATH,
            embeddings=embeddings
        )
    
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            'k': 10,
            'fetch_k': 20,
            'lambda_mult': 0.5
            }
    )
    
    print("검색기 생성 완료")
    return retriever