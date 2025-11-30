#!/bin/bash
# 모든 RAG 시스템의 FAISS 인덱스 생성 스크립트

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 가상환경 활성화
if [ -d "rag-env" ]; then
    echo "가상환경 활성화 중..."
    source rag-env/bin/activate
else
    echo "가상환경 'rag-env'를 찾을 수 없습니다."
    exit 1
fi

echo "=== FAISS 인덱스 생성 시작 ==="
echo ""

# 1. Member RAG 인덱스 생성
echo "[1/3] Member RAG 인덱스 생성 중..."
python member/vector_rag/embedding/embed.py
if [ $? -eq 0 ]; then
    echo "Member RAG 인덱스 생성 완료"
else
    echo "Member RAG 인덱스 생성 실패"
fi
echo ""

# 2. Contest_jw RAG 인덱스 생성
echo "[2/3] Contest_jw RAG 인덱스 생성 중..."
python contest_jw/create_faiss_index.py
if [ $? -eq 0 ]; then
    echo "Contest_jw RAG 인덱스 생성 완료"
else
    echo "Contest_jw RAG 인덱스 생성 실패"
fi
echo ""

# 3. Project RAG 인덱스 생성
echo "[3/3] Project RAG 인덱스 생성 중..."
python project/project_rag/build_index.py
if [ $? -eq 0 ]; then
    echo "Project RAG 인덱스 생성 완료"
else
    echo "Project RAG 인덱스 생성 실패"
fi
echo ""

echo "=== 모든 인덱스 생성 완료 ==="
echo ""
echo "생성된 인덱스 확인:"
ls -lh member/hybrid_rag/rag_faiss_index/ 2>/dev/null | head -5
ls -lh contest_jw/rag_faiss_index/ 2>/dev/null | head -5
ls -lh project/project_rag/rag_faiss_index/ 2>/dev/null | head -5

