import os
import sys
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_experimental.text_splitter import SemanticChunker
from langchain.schema import Document

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# 절대 import로 변경
from member.vector_rag.preprocess.pre1 import curri_docs, memb_docs
from member.vector_rag.preprocess.pre2 import bita_docs

load_dotenv()
all_docs = curri_docs + memb_docs + bita_docs

# === 임베딩 및 시맨틱 청킹 초기화 ===
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
splitter = SemanticChunker(embeddings, breakpoint_threshold_type="percentile")

# === 문서 쪼개기 (문장 의미 단위로 분리) ===
chunked_docs = []
for doc in all_docs:
    chunks = splitter.split_text(doc.page_content)
    for i, chunk in enumerate(chunks):
        chunked_docs.append(
            Document(
                page_content=chunk,
                metadata={**doc.metadata, "chunk_id": i}
            )
        )

print(f"총 {len(all_docs)}개 문서 → {len(chunked_docs)}개 의미 청크로 분할 완료")

# === FAISS 벡터 스토어 생성 ===
vectorstore = FAISS.from_documents(chunked_docs, embeddings)

# hybrid_rag/rag_faiss_index에 저장
SAVE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../hybrid_rag/rag_faiss_index'))
vectorstore.save_local(SAVE_PATH)

print(f"semantic 청킹 + 임베딩 완료 및 {SAVE_PATH}에 저장됨")