# utils/document_processor.py

import re
from typing import List, Dict
from langchain_core.documents import Document
from .data_loader import load_json_data


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


def create_all_documents(data_sources: List[Dict]) -> List[Document]:
    """모든 데이터 소스를 Document로 변환"""
    all_documents = []
    
    for source in data_sources:
        print(f"\n처리 중: {source['platform']} ({source['type']})")
        
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
                print(f"   오류: {e}")
        
        print(f"   {len(docs)}개 Document 생성")
        all_documents.extend(docs)
    
    return all_documents


def remove_duplicates(documents: List[Document]) -> List[Document]:
    """중복 문서 제거 (제목 기준)"""
    
    print("=" * 70)
    print("중복 데이터 제거")
    print("=" * 70)
    
    print(f"\n원본 문서: {len(documents)}개")
    
    # 제목 기준 중복 확인
    seen_titles = {}
    duplicates = []
    
    for i, doc in enumerate(documents):
        title = doc.metadata.get('title', f'Unknown_{i}')
        
        if title in seen_titles:
            duplicates.append((i, title, seen_titles[title]))
        else:
            seen_titles[title] = i
    
    print(f"중복 발견: {len(duplicates)}개")
    
    if duplicates:
        print(f"\n중복 예시 (처음 5개):")
        for i, (idx, title, orig_idx) in enumerate(duplicates[:5], 1):
            print(f"  {i}. '{title[:50]}'")
            print(f"     원본 인덱스: {orig_idx}, 중복 인덱스: {idx}")
    
    # 중복 제거 (제목 기준)
    unique_docs = []
    seen_titles = set()
    
    for doc in documents:
        title = doc.metadata.get('title', '')
        
        if title not in seen_titles:
            unique_docs.append(doc)
            seen_titles.add(title)
    
    print(f"\n중복 제거 완료!")
    print(f"   원본: {len(documents)}개")
    print(f"   제거 후: {len(unique_docs)}개")
    print(f"   제거됨: {len(documents) - len(unique_docs)}개")
    print("=" * 70)
    
    return unique_docs