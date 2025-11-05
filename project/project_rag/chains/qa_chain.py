from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.schema import BaseRetriever, Document
from typing import List, Any
from config.settings import OPEN_API_KEY
from retrievers.vector_retriever import get_vector_retriever
from retrievers.bm25_retriever import get_bm25_retriever
from prompts.question_prompts import prompt


class HybridRetriever(BaseRetriever):

    faiss_retriever: Any
    bm25_retriever: Any

    def get_relevant_documents(self, query: str) -> List[Document]:
        faiss_docs = self.faiss_retriever.get_relevant_documents(query)
        bm25_docs = self.bm25_retriever.get_relevant_documents(query)
        
        all_docs = {d.page_content: d for d in faiss_docs + bm25_docs}
        return list(all_docs.values())

    async def aget_relevant_documents(self, query: str) -> List[Document]:
        return self.get_relevant_documents(query)


def create_hybrid_chain(query=None):
    print("QA 체인을 생성 중...")

    faiss_retriever = get_vector_retriever()
    bm25_retriever = get_bm25_retriever()

    hybrid_retriever = HybridRetriever(
        faiss_retriever=faiss_retriever,
        bm25_retriever=bm25_retriever
    )

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.5,
            openai_api_key=OPEN_API_KEY
        ),
        chain_type="stuff",
        retriever=hybrid_retriever,
        chain_type_kwargs={"prompt": prompt}
    )

    print("QA 체인 생성 완료")
    return chain
