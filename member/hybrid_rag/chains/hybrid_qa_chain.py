from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from config.settings import OPENAI_API_KEY
from retrievers.hybrid_retriever import get_hybrid_retriever
from prompts.q_prompts import question_prompt
from prompts.combine_prompts import combine_prompt

def create_hybrid_qa_chain(query=None):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.2
    )
    retriever = get_hybrid_retriever(query)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="map_reduce",
        chain_type_kwargs={
            "question_prompt": question_prompt,
            "combine_prompt": combine_prompt
        }
    )
    print("[Hybrid QA Chain] 생성 완료")
    return qa_chain