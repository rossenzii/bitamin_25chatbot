from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from retrievers.vector_retriever import get_vector_retriever
from retrievers.bm25_retriever import get_bm25_retriever
import numpy as np
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


# === 2. 하이브리드 검색기 (벡터 중심 가중치 조정) ===
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
            weights = [0.1, 0.9]
        else:
            weights = [0.5, 0.5]

    hybrid_retriever = EnsembleRetriever( # 2 검색기를 하나로 합침
        retrievers=[bm25_retriever, vector_retriever],
        weights=weights
    )
    
    for r in hybrid_retriever.retrievers:
        if hasattr(r, "search_kwargs"):
            r.search_kwargs["k"] = 5  # 문서 5개로 증가 (MT 설명+사례 모두 포함)
    return hybrid_retriever