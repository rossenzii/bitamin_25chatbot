from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import JSONLoader
from config.settings import DATA_DIR_PATH
import os

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