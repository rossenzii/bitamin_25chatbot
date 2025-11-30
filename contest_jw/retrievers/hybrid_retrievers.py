import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever

from config.settings import FAISS_INDEX_PATH, OPENAI_API_KEY

# ========================================
# Lazy 로딩용 전역 변수
# ========================================
_vectorstore = None
_bm25_retriever = None
_embeddings = None


# ========================================
# 1) FAISS 인덱스 로드
# ========================================
def _load_faiss_index():
    """FAISS 인덱스를 로드 (lazy loading)"""
    global _vectorstore, _embeddings

    if _vectorstore is None:
        print("FAISS 인덱스 로드 중...")

        if not Path(FAISS_INDEX_PATH).exists():
            raise FileNotFoundError(
                f"FAISS 인덱스를 찾을 수 없습니다: {FAISS_INDEX_PATH}\n"
                f"먼저 'python create_faiss_index.py'를 실행하여 인덱스를 생성하세요."
            )

        _embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        )

        # 버전별 호환 처리
        try:
            _vectorstore = FAISS.load_local(
                folder_path=FAISS_INDEX_PATH,
                embeddings=_embeddings,
                allow_dangerous_deserialization=True,
            )
        except TypeError:
            _vectorstore = FAISS.load_local(
                folder_path=FAISS_INDEX_PATH,
                embeddings=_embeddings,
            )

        print("FAISS 로드 완료!")

    return _vectorstore, _embeddings


# ========================================
# 2) BM25 Retriever 로드
# ========================================
def _load_bm25_retriever():
    """BM25 Retriever 생성 (lazy loading)"""
    global _bm25_retriever

    if _bm25_retriever is None:
        print("BM25 Retriever 설정 중...")

        vectorstore, _ = _load_faiss_index()
        # FAISS 안의 모든 문서를 가져와서 BM25 인덱스를 만든다
        all_docs = vectorstore.similarity_search("", k=10000)

        if not all_docs:
            raise ValueError("FAISS 인덱스에 문서가 없습니다.")

        _bm25_retriever = BM25Retriever.from_documents(all_docs, k=10)

        print(f"BM25 Retriever 준비 완료! (문서: {len(all_docs)}개)")

    return _bm25_retriever


# ========================================
# 3) 질문 분석 → 토픽 분류
# ========================================
def analyze_query(query: str) -> str:
    """질문 의도를 분석하여 카테고리 반환"""
    q = query.lower()

    if any(w in q for w in ["대외활동", "서포터즈", "기자단", "앰버서더", "리포터", "홍보대사"]):
        return "activity"
    elif any(w in q for w in ["공모전", "대회", "경진대회", "챌린지", "competition"]):
        return "competition"
    elif any(w in q for w in ["강의", "강좌", "수업", "배우", "공부", "학습", "튜토리얼", "입문", "기초"]):
        return "education"
    elif any(w in q for w in ["추천", "찾아", "있어", "알려줘", "소개"]):
        return "recommendation"
    else:
        return "general"


# ========================================
# 4) 메타데이터 필터 생성
# ========================================
def get_search_filter(query: str) -> Optional[Dict[str, Any]]:
    """질문에 따라 메타데이터 필터 생성"""
    topic = analyze_query(query)

    if topic == "activity":
        return {"type": "activity"}
    elif topic == "competition":
        return {"type": "competition"}
    elif topic == "education":
        return {"type": "education"}
    else:
        return None


# ========================================
# 5) 우리가 직접 만든 HybridRetriever
#    (BaseRetriever 상속 X, EnsembleRetriever 사용 X)
# ========================================
class HybridRetriever:
    def __init__(
        self,
        vectorstore,
        bm25_retriever,
        weights: List[float],
        search_filter: Optional[Dict[str, Any]] = None,
        k: int = 10,
    ):
        self.vectorstore = vectorstore
        self.bm25 = bm25_retriever
        self.weights = weights
        self.search_filter = search_filter
        self.k = k

    def get_relevant_documents(self, query: str) -> List[Document]:
        """FAISS + BM25를 단순 가중치 기반으로 섞어서 문서 반환"""

        # 1) FAISS 검색
        faiss_kwargs: Dict[str, Any] = {}
        if self.search_filter:
            # FAISS 메타데이터 필터 지원 시 사용
            faiss_kwargs["filter"] = self.search_filter

        faiss_docs = self.vectorstore.similarity_search(
            query,
            k=self.k,
            **faiss_kwargs,
        )

        # 2) BM25 검색
        bm25_docs = self.bm25.get_relevant_documents(query)[: self.k]

        # 3) 가중치 기반으로 섞기 (FAISS vs BM25 비율)
        w_vec, w_bm = self.weights
        total_w = w_vec + w_bm if (w_vec + w_bm) > 0 else 1.0
        ratio_vec = w_vec / total_w

        target_vec = max(1, int(self.k * ratio_vec))
        target_bm = self.k - target_vec

        result: List[Document] = []
        seen = set()

        def add_docs(docs: List[Document], limit: int):
            added = 0
            for d in docs:
                key = (d.page_content, tuple(sorted(d.metadata.items())))
                if key in seen:
                    continue
                seen.add(key)
                result.append(d)
                added += 1
                if len(result) >= self.k or added >= limit:
                    break

        # 우선순위: 벡터 → BM25
        add_docs(faiss_docs, target_vec)
        if len(result) < self.k:
            add_docs(bm25_docs, target_bm)
        # 그래도 부족하면 나머지 채우기
        if len(result) < self.k:
            add_docs(bm25_docs, self.k - len(result))

        return result[: self.k]


# ========================================
# 6) Hybrid Retriever 생성 함수
# ========================================
def get_hybrid_retriever(query: str = None):
    """
    질문 의도에 맞춰 가중치와 필터를 동적으로 조정
    Returns:
        hybrid_retriever, topic, weights, search_filter
    """
    vectorstore, _ = _load_faiss_index()
    bm25_retriever = _load_bm25_retriever()

    topic = "general"
    search_filter = None
    weights = [0.3, 0.7]  # [FAISS, BM25]

    if query:
        topic = analyze_query(query)
        search_filter = get_search_filter(query)

        if topic in ("activity", "competition"):
            weights = [0.4, 0.6]
        elif topic == "education":
            weights = [0.3, 0.7]
        elif topic == "recommendation":
            weights = [0.2, 0.8]
        else:
            weights = [0.3, 0.7]

    hybrid_retriever = HybridRetriever(
        vectorstore=vectorstore,
        bm25_retriever=bm25_retriever,
        weights=weights,
        search_filter=search_filter,
        k=10,
    )

    return hybrid_retriever, topic, weights, search_filter


# ========================================
# 7) 필터링 통합 함수 (기존 인터페이스 유지)
# ========================================
def get_filtered_results(query: str, top_k: int = 10):
    """
    Hybrid 검색 + 타입 필터

    Returns:
        (docs, topic, weights)
    """
    retriever, topic, weights, search_filter = get_hybrid_retriever(query)
    docs = retriever.get_relevant_documents(query)

    # 혹시 search_filter가 type 기반이면 한 번 더 안전하게 필터링
    if search_filter and "type" in search_filter:
        target_type = search_filter["type"]
        docs = [d for d in docs if d.metadata.get("type") == target_type]

    return docs[:top_k], topic, weights