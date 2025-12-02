import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import JSONLoader

# 상대 import를 절대 import로 변경
try:
    from project.project_rag.config.settings import DATA_DIR_PATH
except ImportError:
    # 상대 import fallback (로컬 실행 시)
    from config.settings import DATA_DIR_PATH

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