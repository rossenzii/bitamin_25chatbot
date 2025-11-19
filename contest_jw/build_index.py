# ========================================
# OpenAI 임베딩 모델 준비
# ========================================
print("=" * 70)
print("OpenAI 임베딩 모델 로드")
print("=" * 70)

from langchain_openai import OpenAIEmbeddings
import os

# API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    print(" OPENAI_API_KEY가 설정되지 않았습니다!")
    raise ValueError("OPENAI_API_KEY를 먼저 설정하세요")

print("\n OpenAI 임베딩 모델 로드 중...")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",  # 빠르고 저렴한 모델
    # model="text-embedding-3-large",  # 더 좋은 성능 (비용 2배)
)

print(" OpenAI 임베딩 모델 로드 완료!")

# 테스트
print("\n 임베딩 테스트 중...")
test_vector = embeddings.embed_query("테스트 문장입니다")
print(f" 벡터 차원: {len(test_vector)}차원")
print(f"   (text-embedding-3-small: 1536차원)")

# Chunking 하지 않고 원본 그대로 사용
chunked_docs = documents

print(f"\n 통계:")
print(f"   총 문서: {len(chunked_docs):,}개")

# 문서 길이 통계
lengths = [len(doc.page_content) for doc in chunked_docs[:100]]
avg_length = sum(lengths) / len(lengths) if lengths else 0

print(f"   평균 길이: {avg_length:.0f}자")
print(f"\n 공모전/강의 데이터는 이미 짧아서 Chunking을 생략합니다.")
print("   (Chunking은 긴 문서에만 필요합니다)")

print("=" * 70)

# ========================================
# FAISS 인덱스 생성
# ========================================
print("=" * 70)
print("FAISS 인덱스 생성")
print("=" * 70)

from langchain_community.vectorstores import FAISS

print(f"\n 벡터화할 문서: {len(chunked_docs)}개")
print(" 벡터 생성 중... (시간이 걸릴 수 있습니다)")

# FAISS 벡터스토어 생성
vectorstore = FAISS.from_documents(
    chunked_docs,
    embeddings
)

# 저장 경로
FAISS_INDEX_PATH = "/Users/jinwoong/Desktop/coding/bitamin/nlp_project_2/faiss_index"

# 저장
print(f"\n FAISS 인덱스 저장 중...")
vectorstore.save_local(FAISS_INDEX_PATH)

print(f"\n FAISS 인덱스 생성 및 저장 완료!")
print(f"   경로: {FAISS_INDEX_PATH}")
print(f"   문서: {len(chunked_docs)}개")
print("=" * 70)