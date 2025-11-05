from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
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
        search_kwargs={"k": 50, "fetch_k": 100, "lambda_mult": 0.7}  # k:5로 증가 (MT 설명+사례 모두 포함)
    )
    return retriever, vectorstore