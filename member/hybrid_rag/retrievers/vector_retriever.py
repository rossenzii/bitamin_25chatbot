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
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 20, "lambda_mult": 0.7}
    )
    print("[Vector retriever] 로드 완료")
    return retriever, vectorstore