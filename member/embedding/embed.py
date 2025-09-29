import os
from dotenv import load_dotenv
from member.preprocess.pre1 import curri_docs, memb_docs
from member.preprocess.pre2 import bita_docs
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
all_docs = curri_docs + memb_docs + bita_docs

# === OpenAI 임베딩 생성 ===
embeddings = OpenAIEmbeddings(openai_api_key=api_key)
vectorstore = FAISS.from_documents(all_docs, embeddings) # 벡터 스토어

# === 저장 ===
vectorstore.save_local("./rag_faiss_index")

print("임베딩 완료 및 저장됨")