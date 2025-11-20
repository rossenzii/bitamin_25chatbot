from langchain_openai import ChatOpenAI
from langchain.schema import BaseRetriever, Document
from typing import List, Any
from config.settings import OPENAI_API_KEY
from retrievers.vector_retriever import get_vector_retriever
from retrievers.bm25_retriever import get_bm25_retriever
from chains.question_classifier import create_question_classifier, create_type_chains
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

class HybridRetriever(BaseRetriever):
    faiss_retriever: Any
    bm25_retriever: Any

    def _get_relevant_documents(self, query: str) -> List[Document]:
        faiss_docs = self.faiss_retriever.invoke(query)
        bm25_docs = self.bm25_retriever.invoke(query)
        all_docs = {d.page_content: d for d in faiss_docs + bm25_docs}
        return list(all_docs.values())

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)

def create_hybrid_chain():
    print("QA 체인을 생성 중...")

    faiss_retriever = get_vector_retriever()
    bm25_retriever = get_bm25_retriever()
    hybrid_retriever = HybridRetriever(faiss_retriever=faiss_retriever, bm25_retriever=bm25_retriever)

    # 질문 분류기 생성
    classifier_chain = create_question_classifier()
    type_branch = create_type_chains()

    # 전체 체인
    preprocess = RunnableLambda(lambda x: {
        "type": classifier_chain.invoke({"question": x["question"]}),
        "context": hybrid_retriever.invoke(x["question"])
    })

    full_chain = preprocess | type_branch | StrOutputParser()

    print("QA 체인 생성 완료")
    return full_chain