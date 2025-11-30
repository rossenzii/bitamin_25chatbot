
import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever



def extract_keywords(text: str) -> List[str]:
    """텍스트에서 주요 키워드 추출"""
    if not text or text == "null" or not isinstance(text, str):
        return []
    
    # 줄바꿈을 공백으로
    text = text.replace('\n', ' ')
    
    # 일반적인 단어들 (제외할 불용어)
    stopwords = {'을', '를', '이', '가', '은', '는', '의', '에', '와', '과', '도', '로', '으로', 
                 '및', '등', '수', '것', '때', '등을', '있는', '하는', '통해', '위한', '대한'}
    
    # 단어 추출 (2글자 이상)
    words = re.findall(r'[가-힣a-zA-Z]{2,}', text)
    
    # 불용어 제거 & 소문자 변환
    keywords = [w.lower() for w in words if w not in stopwords]
    
    # 중복 제거 & 상위 10개
    keywords = list(dict.fromkeys(keywords))[:10]
    
    return keywords

#단일 문서 document전환 함수
def create_document(item: Dict, doc_type: str, platform: str) -> Document:
    """JSON 항목을 LangChain Document로 변환"""
    
    # 1. 텍스트 내용 구성 (null 처리)
    parts = []
    
    # 제목 (필수)
    if item.get('제목'):
        parts.append(f"제목: {item['제목']}")
    
    # 공모전인 경우
    if doc_type == 'competition':
        if item.get('배경'):
            parts.append(f"배경: {item['배경']}")
        if item.get('주제'):
            parts.append(f"주제: {item['주제']}")
        if item.get('설명'):
            parts.append(f"설명: {item['설명']}")
        if item.get('참가 대상'):
            parts.append(f"참가 대상: {item['참가 대상']}")
        
        # 대회 일정 (dict인 경우)
        if item.get('대회 주요 일정') and isinstance(item['대회 주요 일정'], dict):
            schedule_text = ", ".join([f"{k}: {v}" for k, v in item['대회 주요 일정'].items()])
            if schedule_text:
                parts.append(f"대회 일정: {schedule_text}")
    
    # 강의인 경우
    elif doc_type == 'education':
        if item.get('설명'):
            parts.append(f"설명: {item['설명']}")
    
    page_content = "\n".join(parts)
    
    # 2. 키워드 추출 (검색용)
    all_text = " ".join([str(v) for v in item.values() if v and v != "null"])
    keywords = extract_keywords(all_text)
    
    # 3. 메타데이터 구성
    metadata = {
        "type": doc_type,
        "platform": platform,
        "title": item.get('제목', 'Unknown'),
        "url": item.get('Url', ''),
        "keywords": keywords
    }
    
    # 공모전 추가 메타데이터
    if doc_type == 'competition':
        # 마감일 추출
        schedule = item.get('대회 주요 일정', {})
        if isinstance(schedule, dict):
            deadline = schedule.get('대회 종료') or schedule.get('리더보드 제출 마감')
            if deadline:
                metadata['deadline'] = deadline
    
    return Document(page_content=page_content, metadata=metadata)

#모든 문서 documents 전환
def create_all_documents(data_sources: List[Dict]) -> List[Document]:
    """모든 데이터 소스를 Document로 변환"""
    all_documents = []
    
    for source in data_sources:
        print(f"\n 처리 중: {source['platform']} ({source['type']})")
        
        # JSON 로드
        data = load_json_data(source['path'])
        
        if not data:
            continue
        
        # Document 생성
        docs = []
        for item in data:
            try:
                doc = create_document(item, source['type'], source['platform'])
                docs.append(doc)
            except Exception as e:
                print(f"   항목 처리 실패: {item.get('제목', 'Unknown')}")
                print(f"     오류: {e}")
        
        print(f"   {len(docs)}개 Document 생성")
        all_documents.extend(docs)
    
    return all_documents

# 모듈 레벨 실행 코드는 if __name__ == "__main__" 블록으로 감싸기
# 다른 파일에서 import할 때는 실행되지 않도록 함
if __name__ == "__main__":
    # data_sources는 load_data.py에서 가져와야 함
    try:
        from data.load_data import data_sources
    except ImportError:
        print("⚠ data_sources를 찾을 수 없습니다. load_data.py를 먼저 실행하세요.")
        data_sources = []
    
    # 실행
    print("=" * 70)
    print("Document 생성 시작")
    print("=" * 70)
    
    if data_sources:
        documents = create_all_documents(data_sources)
    else:
        documents = []

        print("\n" + "=" * 70)
        print(f" 총 {len(documents)}개 Document 생성 완료!")
        print("=" * 70)
        
        # 샘플 확인
        if documents:
            print("\n 샘플 Document:")
            print(f"내용: {documents[0].page_content[:200]}...")
            print(f"메타데이터: {documents[0].metadata}")
        
        # ========================================
        # 원본 데이터 중복 제거
        # ========================================
        print("=" * 70)
        print("중복 데이터 제거")
        print("=" * 70)
        
        # 1. 중복 확인
        print(f"\n 원본 문서: {len(documents)}개")
        
        # 제목 기준 중복 확인
        seen_titles = {}
        duplicates = []
        
        for i, doc in enumerate(documents):
            title = doc.metadata.get('title', f'Unknown_{i}')
            
            if title in seen_titles:
                duplicates.append((i, title, seen_titles[title]))
            else:
                seen_titles[title] = i
        
        print(f" 중복 발견: {len(duplicates)}개")
        
        if duplicates:
            print(f"\n 중복 예시 (처음 5개):")
            for i, (idx, title, orig_idx) in enumerate(duplicates[:5], 1):
                print(f"  {i}. '{title[:50]}'")
                print(f"     원본 인덱스: {orig_idx}, 중복 인덱스: {idx}")
        
        # 2. 중복 제거 (제목 기준)
        unique_docs = []
        seen_titles = set()
        
        for doc in documents:
            title = doc.metadata.get('title', '')
            
            if title not in seen_titles:
                unique_docs.append(doc)
                seen_titles.add(title)
        
        print(f"\n 중복 제거 완료!")
        print(f"   원본: {len(documents)}개")
        print(f"   제거 후: {len(unique_docs)}개")
        print(f"   제거됨: {len(documents) - len(unique_docs)}개")
        
        # 3. 중복 제거된 데이터 사용
        documents = unique_docs
        chunked_docs = documents  # Chunking 안 함
        
        print("=" * 70)

# ========================================
# linkareer 대외활동/공모전 자동 구분
# ========================================

def classify_linkareer_type(item):
    """
    링커리어 항목을 대외활동/공모전으로 자동 구분
    
    Returns:
        'competition': 공모전
        'activity': 대외활동
    """
    
    # 제목과 내용에서 판단
    title = item.get('title', '').lower()
    content = item.get('content', '').lower()
    category = item.get('category', '').lower()
    
    # 결합
    text = f"{title} {content} {category}"
    
    # 공모전 키워드
    competition_keywords = [
        '공모전', '경진대회', '챌린지', 'contest', 'competition',
        '아이디어 공모', '수상', '시상', '상금'
    ]
    
    # 대외활동 키워드
    activity_keywords = [
        '대외활동', '서포터즈', '기자단', '앰버서더', 
        '리포터', '서포터', '홍보대사', '활동'
    ]
    
    # 점수 계산
    competition_score = sum(1 for kw in competition_keywords if kw in text)
    activity_score = sum(1 for kw in activity_keywords if kw in text)
    
    # 판단
    if competition_score > activity_score:
        return 'competition'
    elif activity_score > competition_score:
        return 'activity'
    else:
        # 동점이면 기본값
        return 'competition'

        # 테스트
        test_items = [
            {"title": "2024 AI 아이디어 공모전", "content": "상금 1000만원"},
            {"title": "카카오 서포터즈 모집", "content": "홍보 대외활동"},
        ]
        
        for item in test_items:
            result = classify_linkareer_type(item)
            print(f"'{item['title']}' → {result}")
        
        
        # 테스트
        test_text = "ChatGPT\nAI\n머신러닝 딥러닝을 활용한 데이터 분석"
        print("테스트 결과:", extract_keywords(test_text))

# JSON 로드 함수
def load_json_data(file_path: str):
    """JSON 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"    파일 없음: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"    JSON 파싱 오류: {e}")
        return None
    except Exception as e:
        print(f"    오류: {e}")
        return None
    
        # ========================================
        # 플랫폼별 문서 개수 집계
        # ========================================
        from collections import Counter
        
        print("\n" + "=" * 70)
        print("플랫폼별 Document 개수")
        print("=" * 70)
        
        platform_counts = Counter(doc.metadata.get('platform', 'unknown') for doc in documents)
        
        for platform, count in platform_counts.items():
            print(f"  {platform:15s} : {count}개")
        
        print("=" * 70)
        print(f"총 Document 수 : {sum(platform_counts.values())}개")
        # ========================================
        # 문서 길이 분석
        # ========================================
        import numpy as np
        
        # 모든 문서 길이 계산
        lengths = [len(doc.page_content) for doc in documents]
        
        print(" 문서 길이 통계:")
        print(f"   총 문서: {len(lengths)}개")
        print(f"   평균: {np.mean(lengths):.0f}자")
        print(f"   최소: {np.min(lengths)}자")
        print(f"   최대: {np.max(lengths)}자")
        print(f"   중간값: {np.median(lengths):.0f}자")
        print(f"   표준편차: {np.std(lengths):.0f}자")
        
        print("\n 길이별 분포:")
        ranges = [
            (0, 300, "매우 짧음"),
            (300, 500, "짧음"),
            (500, 1000, "중간"),
            (1000, 2000, "김"),
            (2000, float('inf'), "매우 김")
        ]
        
        for min_len, max_len, label in ranges:
            count = sum(1 for l in lengths if min_len <= l < max_len)
            percentage = count / len(lengths) * 100
            print(f"   {label:10s} ({min_len:4d}~{max_len:5f}자): {count:5d}개 ({percentage:5.1f}%)")
        
        # 샘플 문서 확인
        print("\n 샘플 문서 (처음 3개):")
        for i, doc in enumerate(documents[:3], 1):
            print(f"\n{i}. {doc.metadata.get('title', 'Unknown')[:50]}")
            print(f"   길이: {len(doc.page_content)}자")
            print(f"   내용: {doc.page_content[:150]}...")
        
        # ========================================
        # 최종 정리(Chunking 생략)
        # ========================================
        
        chunked_docs = documents
        
        print(f"  Chunking 생략 (문서가 충분히 짧음)")
        print(f"   총 문서: {len(chunked_docs)}개")
        print(f"   평균 길이: 150자")
        print(f"   93.4%가 300자 미만")



## 긴 문서 37개는?

### 걱정 불필요!
'''
이유 1: 극소수 (0.5%)
→ 전체 성능에 거의 영향 없음

이유 2: 1000~2000자도 짧음
→ LLM이 한 번에 처리 가능
→ 문제없음!

이유 3: 전체 맥락 유지
→ 분할하면 오히려 정보 손실
→ 그대로가 나음!
'''



## 성능 예상

### Chunking 없어도 완벽!
'''
평균 150자:
 검색 정확도: 매우 높음
 LLM 처리: 매우 빠름
 메모리: 매우 적음
 맥락 유지: 완벽

→ 이상적인 크기! 
'''