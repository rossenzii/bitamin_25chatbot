import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate

# QA Chain import
from chains.qa_chain import create_hybrid_qa_chain

# ========================================
# Main 함수 QA 테스트
# ========================================
print("=" * 70)
print("Main 함수 스타일 QA 테스트")
print("=" * 70)

import traceback

def run_qa_test(query: str, verbose: bool = True):
    """
    Main.py 스타일의 QA 실행 함수
    
    Args:
        query: 사용자 질문
        verbose: 상세 출력 여부
    
    Returns:
        result: 실행 결과 딕셔너리
    """
    
    if verbose:
        print(f"\n{'='*70}")
        print(f" 질문: {query}")
        print('='*70)
    
    try:
        # 1. QA Chain 생성
        qa_chain = create_hybrid_qa_chain(query=query)
        
        # 2. 답변 생성
        result = qa_chain.invoke({"query": query})
        
        # 3. 답변 출력
        answer = result.get("result", "답변을 생성하지 못했습니다.")
        
        if verbose:
            print("\n 답변:")
            print("-" * 70)
            print(answer)
            print("-" * 70)
            
            # 참조 문서 정보
            source_docs = result.get("source_documents", [])
            if source_docs:
                print(f"\n 참조 문서 ({len(source_docs)}개):")
                for i, doc in enumerate(source_docs[:5], 1):
                    title = doc.metadata.get('title', 'Unknown')
                    doc_type = doc.metadata.get('type', 'Unknown')
                    platform = doc.metadata.get('platform', 'Unknown')
                    
                    print(f"\n   [{i}] {title}")
                    print(f"       유형: {doc_type} | 플랫폼: {platform}")
                    
                    # URL이 있으면 출력
                    url = doc.metadata.get('url', '')
                    if url:
                        print(f"        {url}")
        
        return {
            'success': True,
            'query': query,
            'answer': answer,
            'source_documents': result.get("source_documents", []),
            'error': None
        }
        
    except Exception as e:
        if verbose:
            print(f"\n 오류 발생: {str(e)}")
            traceback.print_exc()
        
        return {
            'success': False,
            'query': query,
            'answer': None,
            'source_documents': [],
            'error': str(e)
        }

print(" 테스트 함수 준비 완료!")

# ========================================
# 단일 테스트 실행
# ========================================
print("\n" + "=" * 70)
print("단일 테스트 실행")
print("=" * 70)

# 테스트 질문
test_query = "llm 관렪해서 공모전이나 강의 추천해줄래?"

# 실행
result = run_qa_test(test_query, verbose=True)

print("\n" + "=" * 70)