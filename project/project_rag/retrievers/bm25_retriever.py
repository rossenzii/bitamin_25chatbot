import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import JSONLoader

# 환경 변수 우선 사용 (배포 환경 대응)
DATA_DIR_PATH = [
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "project_txt", "1415V"),
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "project_txt", "1415S")
]

# config import 시도 (선택사항)
try:
    from project.project_rag.config.settings import DATA_DIR_PATH as CONFIG_PATH
    DATA_DIR_PATH = CONFIG_PATH
except ImportError:
    try:
        from config.settings import DATA_DIR_PATH as CONFIG_PATH
        DATA_DIR_PATH = CONFIG_PATH
    except ImportError:
        pass

def get_bm25_retriever():

    docs = []

    paths = DATA_DIR_PATH if isinstance(DATA_DIR_PATH, list) else [DATA_DIR_PATH]

    for path in paths:
        for file_name in os.listdir(path):
            if file_name.endswith(".json"):
                file_path = os.path.join(path, file_name)
                loader = JSONLoader(
                    file_path=file_path,
                    jq_schema=".[]",
                    text_content=False
                )
                docs.extend(loader.load())

    retriever = BM25Retriever.from_documents(docs)
    
    print(f"검색기 생성 완료 (총 {len(docs)}개 문서 로드)")
    
    return retriever