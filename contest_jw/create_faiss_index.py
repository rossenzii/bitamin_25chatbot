#!/usr/bin/env python3
"""
contest_jw FAISS 인덱스 생성 스크립트
실행 방법: python create_faiss_index.py
"""

import sys
import os
import json
from pathlib import Path

# 프로젝트 경로 설정
BASE_DIR = Path(__file__).parent.resolve()  # contest_jw/
PROJECT_ROOT = BASE_DIR.parent.resolve()  # fw_project/ (프로젝트 루트)
sys.path.insert(0, str(BASE_DIR))

print("=" * 70)
print("contest_jw FAISS 인덱스 생성")
print("=" * 70)

# 1. 환경 변수 확인
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("✗ OPENAI_API_KEY가 설정되지 않았습니다!")
    print("  .env 파일에 OPENAI_API_KEY를 추가해주세요.")
    sys.exit(1)

print("✓ 환경 변수 확인 완료")

# 2. 데이터 소스 정의 및 로드
print("\n[1단계] 데이터 로드")
print("-" * 70)

# 프로젝트 루트 기준 상대 경로로 데이터 소스 정의
data_sources = [
    {
        "path": str(PROJECT_ROOT / "tami" / "data_sources" / "dacon" / "dacon.json"),
        "type": "competition",
        "platform": "dacon",
        "description": "데이콘 AI 경진대회"
    },
    {
        "path": str(PROJECT_ROOT / "tami" / "data_sources" / "inflearn" / "inflearn_courses_all.json"),
        "type": "education",
        "platform": "inflearn",
        "description": "인프런 온라인 강의"
    },
    {
        "path": str(PROJECT_ROOT / "tami" / "data_sources" / "lh_compas" / "lh_compas_산학협력.json"),
        "type": "competition",
        "platform": "lh_compas",
        "description": "LH 컴퍼스 산학협력"
    },
    {
        "path": str(PROJECT_ROOT / "tami" / "data_sources" / "lh_compas" / "lh_compas_아이디어공모전.json"),
        "type": "competition",
        "platform": "lh_compas",
        "description": "LH 컴퍼스 아이디어 공모전"
    },
    {
        "path": str(PROJECT_ROOT / "tami" / "data_sources" / "kaggle" / "kaggle_active_korean.json"),
        "type": "competition",
        "platform": "kaggle",
        "description": "Kaggle 경진대회 (한국어)"
    },
    {
        "path": str(PROJECT_ROOT / "tami" / "data_sources" / "linkareer" / "linkareer.json"),
        "type": "auto",  # 자동 판단
        "platform": "linkareer",
        "description": "링커리어 (대외활동/공모전 자동 구분)"
    },
    {
        "path": str(PROJECT_ROOT / "tami" / "data_sources" / "공공데이터포털" / "data_go_kr.json"),
        "type": "competition",
        "platform": "data_go_kr",
        "description": "공공데이터포털 공모전"
    },
]

# linkareer 타입 분류 함수 import
from data.preprocess import classify_linkareer_type

# 실제 데이터 경로 확인 및 로드
all_documents = []

for source in data_sources:
    file_path = source['path']
    platform = source['platform']
    data_type = source['type']
    
    print(f"\n{platform} 로드 중...")
    print(f"  경로: {file_path}")
    
    if not Path(file_path).exists():
        print(f"  ⚠ 파일 없음: {file_path}")
        print(f"    → 이 데이터 소스는 건너뜁니다.")
        continue
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        print(f"  원본: {len(raw_data)}개")
        
        for item in raw_data:
            title = item.get('title', item.get('제목', '제목 없음'))
            content = item.get('content', item.get('description', item.get('설명', '')))
            url = item.get('url', item.get('Url', ''))
            
            # linkareer는 자동 구분
            if platform == 'linkareer' and data_type == 'auto':
                doc_type = classify_linkareer_type(item)
            else:
                doc_type = data_type
            
            from langchain_core.documents import Document
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
        
        print(f"  완료: {len(raw_data)}개")
        
    except Exception as e:
        print(f"  ✗ 오류: {e}")
        import traceback
        traceback.print_exc()
        continue

if not all_documents:
    print("\n✗ 로드된 문서가 없습니다!")
    print("  데이터 경로를 확인하거나 data_sources를 수정해주세요.")
    sys.exit(1)

print(f"\n✓ 총 {len(all_documents)}개 문서 로드 완료")

# 3. 중복 제거 (선택사항)
print("\n[2단계] 중복 제거")
print("-" * 70)

from collections import Counter

# 제목 기준 중복 확인
seen_titles = {}
unique_docs = []

for doc in all_documents:
    title = doc.metadata.get('title', '')
    if title and title not in seen_titles:
        unique_docs.append(doc)
        seen_titles[title] = True

print(f"원본: {len(all_documents)}개")
print(f"중복 제거 후: {len(unique_docs)}개")
print(f"제거됨: {len(all_documents) - len(unique_docs)}개")

documents = unique_docs

# 4. 임베딩 모델 준비
print("\n[3단계] 임베딩 모델 준비")
print("-" * 70)

from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=OPENAI_API_KEY
)

print("✓ OpenAI 임베딩 모델 로드 완료")

# 테스트
test_vector = embeddings.embed_query("테스트")
print(f"✓ 임베딩 테스트 완료 (차원: {len(test_vector)})")

# 5. FAISS 인덱스 생성
print("\n[4단계] FAISS 인덱스 생성")
print("-" * 70)

from langchain_community.vectorstores import FAISS

print(f"벡터화할 문서: {len(documents)}개")
print("벡터 생성 중... (시간이 걸릴 수 있습니다)")

try:
    vectorstore = FAISS.from_documents(
        documents,
        embeddings
    )
    print("✓ FAISS 인덱스 생성 완료")
except Exception as e:
    print(f"✗ FAISS 인덱스 생성 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. 인덱스 저장
print("\n[5단계] 인덱스 저장")
print("-" * 70)

# 저장 경로 설정 (config/settings.py 사용)
from config.settings import FAISS_INDEX_PATH

# 디렉토리 생성
index_dir = Path(FAISS_INDEX_PATH)
index_dir.mkdir(parents=True, exist_ok=True)

print(f"저장 경로: {FAISS_INDEX_PATH}")

try:
    vectorstore.save_local(FAISS_INDEX_PATH)
    print("✓ FAISS 인덱스 저장 완료")
    
    # 저장된 파일 확인
    faiss_file = Path(FAISS_INDEX_PATH) / "index.faiss"
    pkl_file = Path(FAISS_INDEX_PATH) / "index.pkl"
    
    if faiss_file.exists() and pkl_file.exists():
        print(f"✓ 저장된 파일 확인:")
        print(f"  - {faiss_file} ({faiss_file.stat().st_size / 1024 / 1024:.2f} MB)")
        print(f"  - {pkl_file} ({pkl_file.stat().st_size / 1024:.2f} KB)")
    else:
        print("⚠ 저장된 파일을 찾을 수 없습니다.")
        
except Exception as e:
    print(f"✗ FAISS 인덱스 저장 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 7. 완료
print("\n" + "=" * 70)
print("FAISS 인덱스 생성 완료!")
print("=" * 70)
print(f"저장 위치: {FAISS_INDEX_PATH}")
print(f"문서 개수: {len(documents)}개")
print("\n이제 main.py를 실행할 수 있습니다:")
print("  python main.py")

