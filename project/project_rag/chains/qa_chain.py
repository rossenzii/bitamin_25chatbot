import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from langchain_openai import ChatOpenAI
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from typing import List, Any
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 절대 import와 상대 import 모두 시도
try:
    from project.project_rag.config.settings import OPENAI_API_KEY
    from project.project_rag.retrievers.vector_retriever import get_vector_retriever
    from project.project_rag.retrievers.bm25_retriever import get_bm25_retriever
    from project.project_rag.chains.question_classifier import create_question_classifier, create_type_chains
except ImportError:
    try:
        # 상대 import fallback (로컬 실행 시)
        from config.settings import OPENAI_API_KEY
        from retrievers.vector_retriever import get_vector_retriever
        from retrievers.bm25_retriever import get_bm25_retriever
        from chains.question_classifier import create_question_classifier, create_type_chains
    except ImportError:
        # 환경 변수 사용
        import os
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        from project.project_rag.retrievers.vector_retriever import get_vector_retriever
        from project.project_rag.retrievers.bm25_retriever import get_bm25_retriever
        from project.project_rag.chains.question_classifier import create_question_classifier, create_type_chains

class HybridRetriever(BaseRetriever):
    faiss_retriever: Any
    bm25_retriever: Any

    def _get_relevant_documents(self, query: str) -> List[Document]:
        faiss_docs = self.faiss_retriever.invoke(query)
        bm25_docs = self.bm25_retriever.invoke(query)
        # 중복 제거 및 병합
        all_docs = {d.page_content: d for d in faiss_docs + bm25_docs}
        return list(all_docs.values())

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        return self._get_relevant_documents(query)

def create_hybrid_chain():
    print("QA 체인을 생성 중...")

    faiss_retriever = get_vector_retriever()
    bm25_retriever = get_bm25_retriever()
    hybrid_retriever = HybridRetriever(faiss_retriever=faiss_retriever, bm25_retriever=bm25_retriever)

<<<<<<< HEAD
    condense_chain = create_condense_question_chain() # 질문 재구성 체인
=======
>>>>>>> main
    classifier_chain = create_question_classifier()   # 질문 유형 분류기
    type_branch = create_type_chains()                # 유형별 답변 체인

    def retrieve_and_format(query):
        docs = hybrid_retriever.invoke(query)
        return "\n\n".join([
            f"[DOC {i}]\n"
            f"title: {doc.metadata.get('title', '')}\n"
            f"info: {doc.metadata.get('info', '')}\n"
            f"kategorie: {doc.metadata.get('kategorie', '')}\n"
            f"text: {doc.page_content}"
            for i, doc in enumerate(docs)
        ])
    
    main_chain = (
<<<<<<< HEAD
        RunnablePassthrough.assign(
            standalone_question=condense_chain 
        )
        | RunnablePassthrough.assign(
            context=lambda x: retrieve_and_format(x["standalone_question"]),
            type=lambda x: classifier_chain.invoke({"question": x["standalone_question"]})
        )
        | RunnablePassthrough.assign(
            question=lambda x: x["standalone_question"]
        )
=======
        RunnableLambda(lambda x: {
            "question": x["question"],
            "type": classifier_chain.invoke({"question": x["question"]}),
            "context": retrieve_and_format(x["question"])
        })
>>>>>>> main
        | type_branch 
        | StrOutputParser()
    )

    print("QA 체인 생성 완료")
    return main_chain