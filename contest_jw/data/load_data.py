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
# 데이터 소스 정의 (전체)
# ========================================
print("=" * 70)
print("데이터 소스 정의")
print("=" * 70)

data_sources = [
    # ========= 기존 데이터 =========
    {
        "path": "/Users/jinwoong/Desktop/coding/Bitamin/nlp_project_2/dataset/dacon/dacon.json",
        "type": "competition",
        "platform": "dacon",
        "description": "데이콘 AI 경진대회"
    },
    {
        "path": "/Users/jinwoong/Desktop/coding/Bitamin/nlp_project_2/dataset/Inflearn/inflearn_courses_all.json",
        "type": "education",
        "platform": "inflearn",
        "description": "인프런 온라인 강의"
    },
    
    # ========= 새로 추가 =========
    {
        "path": "/Users/jinwoong/Desktop/coding/Bitamin/nlp_project_2/dataset/lh_compas/lh_compas_산학협력.json",
        "type": "competition",
        "platform": "lh_compas",
        "description": "LH 컴퍼스 산학협력"
    },
    {
        "path": "/Users/jinwoong/Desktop/coding/Bitamin/nlp_project_2/dataset/lh_compas/lh_compas_아이디어공모전.json",
        "type": "competition",
        "platform": "lh_compas",
        "description": "LH 컴퍼스 아이디어 공모전"
    },
    {
        "path": "/Users/jinwoong/Desktop/coding/Bitamin/nlp_project_2/dataset/kaggle/kaggle_active_korean.json",
        "type": "competition",
        "platform": "kaggle",
        "description": "Kaggle 경진대회 (한국어)"
    },
    {
        "path": "/Users/jinwoong/Desktop/coding/Bitamin/nlp_project_2/dataset/linkareer/linkareer.json",
        "type": "auto",  # 자동 판단
        "platform": "linkareer",
        "description": "링커리어 (대외활동/공모전 자동 구분)"
    },
    {
        "path": "/Users/jinwoong/Desktop/coding/Bitamin/nlp_project_2/dataset/공공데이터포털/data_go_kr.json",
        "type": "competition",
        "platform": "data_go_kr",
        "description": "공공데이터포털 공모전"
    },
]

print(f"\n총 {len(data_sources)}개 데이터 소스")
for i, source in enumerate(data_sources, 1):
    print(f"  [{i}] {source['platform']:15s} - {source['description']}")

print("=" * 70)

# ========================================
# 전체 데이터 로드
# ========================================
print("=" * 70)
print("전체 데이터 로드")
print("=" * 70)

import json
from langchain.schema import Document

all_documents = []

for source in data_sources:
    platform = source['platform']
    data_type = source['type']
    file_path = source['path']
    
    print(f"\n {platform} 로드 중...")
    
    try:
        # JSON 로드
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        print(f"   원본: {len(raw_data)}개")
        
        # 데이터 처리
        for item in raw_data:
            title = item.get('title', '제목 없음')
            content = item.get('content', item.get('description', ''))
            url = item.get('url', '')
            
            # linkareer는 자동 구분
            if platform == 'linkareer' and data_type == 'auto':
                doc_type = classify_linkareer_type(item)
            else:
                doc_type = data_type
            
            # Document 생성
            doc = Document(
                page_content=f"제목: {title}\n\n{content}",
                metadata={
                    'title': title,
                    'type': doc_type,
                    'platform': platform,
                    'url': url,
                }
            )
            all_documents.append(doc)
        
        print(f"    {len(raw_data)}개 완료")
        
    except FileNotFoundError:
        print(f"    파일 없음: {file_path}")
    except Exception as e:
        print(f"    오류: {e}")

print("\n" + "=" * 70)
print(f" 총 {len(all_documents)}개 문서 로드")

# 통계
from collections import Counter
platform_counts = Counter([d.metadata['platform'] for d in all_documents])
type_counts = Counter([d.metadata['type'] for d in all_documents])

print("\n 플랫폼별:")
for p, c in platform_counts.most_common():
    print(f"   {p:15s}: {c:4d}개")

print("\n 타입별:")
for t, c in type_counts.most_common():
    print(f"   {t:15s}: {c:4d}개")

print("=" * 70)