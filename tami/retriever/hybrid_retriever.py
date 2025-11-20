# retriever/hybrid_retriever.py

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from typing import List
from langchain.schema import Document


class HybridRetriever:
    """Hybrid Retriever (Vector + BM25)"""
    
    def __init__(self, vectorstore, documents: List[Document]):
        """
        Args:
            vectorstore: FAISS 벡터스토어
            documents: 전체 Document 리스트 (BM25용)
        """
        self.vectorstore = vectorstore
        self.documents = documents
        
        print("=" * 70)
        print("Hybrid Retriever 설정")
        print("=" * 70)
        
        # BM25 Retriever 생성
        print("\nBM25 Retriever 설정 중...")
        self.bm25_retriever = BM25Retriever.from_documents(
            documents,
            k=10
        )
        print("BM25 Retriever 준비!")
        print("\nHybrid Retriever 함수 준비 완료!")
        print("=" * 70)
    
    def analyze_query(self, query: str) -> str:
        """질문 의도를 분석하여 카테고리 반환"""
        q = query.lower()
        
        if any(w in q for w in ["대외활동", "서포터즈", "기자단", "앰버서더", "리포터", "서포터", "홍보대사"]):
            return "activity"
        
        elif any(w in q for w in ["공모전", "대회", "경진대회", "챌린지", "competition"]):
            return "competition"
        
        elif any(w in q for w in ["강의", "강좌", "수업", "배우", "공부", "학습", "튜토리얼", "입문", "기초"]):
            return "education"
        
        elif any(w in q for w in ["추천", "찾아", "있어", "알려줘", "소개"]):
            return "recommendation"
        
        else:
            return "general"
    
    def get_search_filter(self, query: str):
        """질문에 따라 메타데이터 필터 생성"""
        topic = self.analyze_query(query)
        
        if topic == "activity":
            return {"type": "activity"}
        elif topic == "competition":
            return {"type": "competition"}
        elif topic == "education":
            return {"type": "education"}
        else:
            return None
    
    def get_hybrid_retriever(self, query: str = None):
        """
        질문 의도에 맞춰 가중치와 필터를 동적으로 조정
        
        Args:
            query: 사용자 질문
        
        Returns:
            hybrid_retriever, topic, weights, search_filter
        """
        
        # 기본 설정
        weights = [0.3, 0.7]
        topic = "general"
        search_filter = None
        
        if query:
            topic = self.analyze_query(query)
            search_filter = self.get_search_filter(query)
            
            # 주제별 가중치 조정
            if topic == "activity":
                weights = [0.4, 0.6]
            elif topic == "competition":
                weights = [0.4, 0.6]
            elif topic == "education":
                weights = [0.3, 0.7]
            elif topic == "recommendation":
                weights = [0.2, 0.8]
            else:
                weights = [0.3, 0.7]
        
        # Vector Retriever 생성 (필터 적용)
        vector_search_kwargs = {
            "k": 10,
            "fetch_k": 100,
            "lambda_mult": 0.7
        }
        
        if search_filter:
            vector_search_kwargs["filter"] = search_filter
        
        vector_retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs=vector_search_kwargs
        )
        
        # Ensemble Retriever
        hybrid_retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever, vector_retriever],
            weights=weights
        )
        
        return hybrid_retriever, topic, weights, search_filter
    
    def get_filtered_results(self, query: str, top_k: int = 10):
        """
        Hybrid 검색 + 타입 필터
        
        Args:
            query: 사용자 질문
            top_k: 최종 반환 개수
        
        Returns:
            필터링된 문서 리스트, topic, weights
        """
        
        # 1. Hybrid 검색
        retriever, topic, weights, search_filter = self.get_hybrid_retriever(query)
        docs = retriever.get_relevant_documents(query)
        
        # 2. 타입 필터링 (BM25 결과에 적용)
        if search_filter:
            target_type = search_filter.get("type")
            docs = [doc for doc in docs if doc.metadata.get("type") == target_type]
        
        # 3. Top K
        docs = docs[:top_k]
        
        return docs, topic, weights