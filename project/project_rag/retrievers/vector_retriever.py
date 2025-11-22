from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from config.settings import OPENAI_API_KEY, FAISS_INDEX_PATH

def get_vector_retriever():

    embeddings=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    vectorstore=FAISS.load_local(
        folder_path=FAISS_INDEX_PATH,
        embeddings=embeddings,
        allow_dangerous_deserialization=True
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