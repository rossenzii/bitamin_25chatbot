import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_experimental.text_splitter import SemanticChunker
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# ========================================
# 셀 11: Hybrid Retriever (수정 버전)
# ========================================
print("=" * 70)
print("Hybrid Retriever 설정")
print("=" * 70)

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import numpy as np

# 1. FAISS 로드
print("\nFAISS 인덱스 로드 중...")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = FAISS.load_local(
    "/Users/jinwoong/Desktop/coding/Bitamin/nlp_project_2/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

print("FAISS 로드 완료!")

# 2. 질문 분석 함수
def analyze_query(query: str) -> str:
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

# 3. 메타데이터 필터 생성 함수
def get_search_filter(query: str):
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

# 4. BM25 Retriever (전역으로 먼저 생성)
print("\nBM25 Retriever 설정 중...")

all_docs = []
for doc_id in range(len(chunked_docs)):
    all_docs.append(chunked_docs[doc_id])

bm25_retriever = BM25Retriever.from_documents(
    all_docs,
    k=10
)

print("BM25 Retriever 준비!")

# 5. Hybrid Retriever 생성 함수
def get_hybrid_retriever(query: str = None):
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
        topic = analyze_query(query)
        search_filter = get_search_filter(query)
        
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
    
    vector_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs=vector_search_kwargs
    )
    
    # Ensemble Retriever
    hybrid_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=weights
    )
    
    return hybrid_retriever, topic, weights, search_filter

# 6. 필터링 통합 함수
def get_filtered_results(query: str, top_k: int = 10):
    """
    Hybrid 검색 + 타입 필터
    
    Args:
        query: 사용자 질문
        top_k: 최종 반환 개수
    
    Returns:
        필터링된 문서 리스트
    """
    
    # 1. Hybrid 검색
    retriever, topic, weights, search_filter = get_hybrid_retriever(query)
    docs = retriever.get_relevant_documents(query)
    
    # 2. 타입 필터링 (BM25 결과에 적용)
    if search_filter:
        target_type = search_filter.get("type")
        docs = [doc for doc in docs if doc.metadata.get("type") == target_type]
    
    # 3. Top K
    docs = docs[:top_k]
    
    return docs, topic, weights

print("\nHybrid Retriever 함수 준비 완료!")
