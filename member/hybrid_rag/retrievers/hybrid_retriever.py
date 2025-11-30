import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import List
import numpy as np

# 상대 import를 절대 import로 변경
try:
    from member.hybrid_rag.retrievers.vector_retriever import get_vector_retriever
    from member.hybrid_rag.retrievers.bm25_retriever import get_bm25_retriever
except ImportError:
    # 상대 import fallback (로컬 실행 시)
    from retrievers.vector_retriever import get_vector_retriever
    from retrievers.bm25_retriever import get_bm25_retriever
# hybrid_retriever: 문서 검색기

# === 1. 의미 기반 주제 분류 (Embedding Similarity) ===
def analyze_query(query: str) -> str:
    q = query.lower()
    # 키워드 우선 분류
    if any(w in q for w in ["지원", "테스트", "ot", "인스타", "대회", "현직자", "홈커밍", "규칙", "모집", "문의", "공모전", "수상", "mt", "소모임", "프로젝트", "데이터톤", "컨퍼런스"]):
        return "activity"
    elif any(w in q for w in ["멤버", "회원", "운영진", "mbti", "성별", "학교","나이","역할","부서"]):
        return "member"
    elif any(w in q for w in ["세션", "커리큘럼", "스터디", "수업", "강의", "방학","교육"]):
        return "curriculum"

    # 그 외는 의미 기반(임베딩)으로 분류
    categories = {
        "member": "멤버나 운영진 개인의 정보, 역할, 인원 구성, MBTI, 나이, 학교, 부서에 대한 질문",
        "curriculum": "세션, 스터디, 강의, 커리큘럼, 학습 내용, 발표 주제 등 교육 관련 질문",
        "activity": "mt, 소모임, ot, 프로젝트, 컨퍼런스, 데이터톤, 공모전, 행사 일정, 동아리 활동이나 이벤트 관련 질문",
        "general": "기타 일반적인 질문이나 단순 정보 요청"
    }
    # OpenAI 임베딩 초기화
    emb = OpenAIEmbeddings()
    query_vec = np.array(emb.embed_query(query))
    sims = {}
    # 코사인 유사도 계산
    for k, desc in categories.items():
        cat_vec = np.array(emb.embed_query(desc))
        sim = np.dot(query_vec, cat_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(cat_vec))
        sims[k] = sim

    topic = max(sims, key=sims.get) # 가장 유사도가 높은 주제 선택
    return topic


# === 2. HybridRetriever 클래스 ===
class HybridRetriever:
    def __init__(self, bm25_retriever, vector_retriever, weights=(0.5, 0.5)):
        self.bm25_retriever = bm25_retriever
        self.vector_retriever = vector_retriever
        self.weights = weights

    def get_relevant_documents(self, query: str):
        # 최신 LangChain retriever 규격 (invoke 사용)
        bm25_docs = self.bm25_retriever.invoke(query)
        vector_docs = self.vector_retriever.invoke(query)
        
        # 두 결과를 병합
        merged_docs = self._merge_scores(bm25_docs, vector_docs)
        
        return merged_docs

    def _merge_scores(self, bm25_docs, vector_docs):
        # 딱 너가 쓰던 방식 그대로 유지하면 됨
        seen = {}
        w_bm25, w_vector = self.weights
        
        for doc in bm25_docs:
            seen[doc.page_content] = seen.get(doc.page_content, 0) + w_bm25 * getattr(doc, 'score', 1)
        
        for doc in vector_docs:
            seen[doc.page_content] = seen.get(doc.page_content, 0) + w_vector * getattr(doc, 'score', 1)
        
        # Document로 다시 묶어서 반환
        merged_list = [
            Document(page_content=content, metadata={"score": score})
            for content, score in seen.items()
        ]
        
        # 점수 기준 정렬
        merged_list.sort(key=lambda x: x.metadata["score"], reverse=True)
        
        return merged_list


# === 3. 하이브리드 검색기 생성 함수 ===
def get_hybrid_retriever(query: str = None):
    """질문 의도에 맞춰 가중치를 동적으로 조정하는 Hybrid Retriever"""
    vector_retriever, vectorstore = get_vector_retriever()
    bm25_retriever = get_bm25_retriever(vectorstore)

    # 기본 가중치
    weights = [0.5, 0.5]  # [BM25, Vector] : 검색기 2개 준비 [의미, 키워드]

    if query:
        topic = analyze_query(query) # 질문 분석

        # 주제별로 의미검색(Vector) 비중을 크게
        if topic == "member":
            weights = [0.4, 0.6]
        elif topic == "curriculum":
            weights = [0.3, 0.7]
        elif topic == "activity":
            weights = [0.4, 0.6]
        else:
            weights = [0.5, 0.5]

    hybrid_retriever = HybridRetriever(
        bm25_retriever=bm25_retriever,
        vector_retriever=vector_retriever,
        weights=tuple(weights)
    )
    
    return hybrid_retriever