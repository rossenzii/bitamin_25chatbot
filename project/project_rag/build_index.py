import os
from glob import glob
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from config.settings import DATA_DIR_PATH, FAISS_INDEX_PATH, OPENAI_API_KEY

# JSON 구조 정의
JQ_SCHEMA = '.[]'
def metadata_function(record: dict, metadata: dict) -> dict:
    metadata['slide_number'] = record.get("slide")
    metadata['source'] = os.path.basename(metadata.get("source", ""))
    metadata['title'] = record.get("title", "")
    metadata['info'] = record.get("info", "") 
    metadata['kategorie'] = record.get("kategorie", "")
    return metadata


def build_and_save_index():
    print("JSON 파일 로드 중..")

    # 모든 JSON 파일 경로 찾기
    json_files = []
    for path in DATA_DIR_PATH:
        json_files.extend(glob(os.path.join(path, "*.json")))
    if not json_files:
        print(f"오류: {DATA_DIR_PATH}에 JSON 파일이 없습니다.")
        return
    
    # 모든 JSON 파일 로드
    all_docs = []
    for file_path in json_files:
        loader = JSONLoader(
            file_path=file_path,
            jq_schema=JQ_SCHEMA,
            text_content=False,
            content_key="text",
            metadata_func=metadata_function
        )

        docs = loader.load()
        
        for doc in docs:
            title = doc.metadata.get("title", "")
            info = doc.metadata.get("info", "")
            kategorie = doc.metadata.get("kategorie", "")
            text = " ".join(doc.page_content) if isinstance(doc.page_content, list) else doc.page_content
            
            doc.page_content = f"제목: {title}\n정보: {info}\n카테고리: {kategorie}\n내용: {text}"
            all_docs.append(doc)
    print(f"총 {len(all_docs)}개 문서 로드 완료")

    # 분할
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(all_docs)

    # embedding 및 FAISS 생성
    print("FAISS 인덱스 생성 및 저장 중..")
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

    # 저장
    vectorstore.save_local(FAISS_INDEX_PATH, index_name="index")
    print("인덱스 저장 완료")

if __name__ == "__main__":
    build_and_save_index()