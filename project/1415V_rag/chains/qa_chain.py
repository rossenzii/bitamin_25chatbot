from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from config.settings import OPEN_API_KEY
from retrievers.vector_retriever import get_vector_retriever
from prompts.question_prompts import prompt

def create_hybrid_chain(query=None):
    print("QA 체인을 생성 중...")

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        openad_api_key=OPEN_API_KEY  
        ),
        chain_type="stuff",
        retriever=get_vector_retriever(query),
        chain_type_kwargs={"prompt": prompt}
    )
    
    print("QA 체인 생성 완료")
    return chain