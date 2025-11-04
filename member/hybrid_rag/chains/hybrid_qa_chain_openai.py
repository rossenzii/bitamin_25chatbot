from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from retrievers.hybrid_retriever import get_hybrid_retriever
from prompts.q_prompts import question_prompt
from config.settings import OPENAI_API_KEY

### hybrid_qa_chain: OpenAI API를 사용하는 버전 (더 나은 한국어 답변)

def create_hybrid_qa_chain(query=None):
    # OpenAI API 사용 (한국어 처리 우수, QA 태스크 최적화)
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # 빠르고 저렴한 모델
        openai_api_key=OPENAI_API_KEY,
        temperature=0.2,  # 일관된 답변
    )
    retriever = get_hybrid_retriever(query)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={
            "prompt": question_prompt
        }
    )

    return qa_chain

