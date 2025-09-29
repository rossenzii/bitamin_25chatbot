import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings(openai_api_key=api_key)
vectorstore = FAISS.load_local("./rag_faiss_index", embeddings, allow_dangerous_deserialization=True)

query = "비타민 동아리 모집 일정 알려줘"
results = vectorstore.similarity_search(query, k=5)

for r in results:
    print(r.page_content, r.metadata)