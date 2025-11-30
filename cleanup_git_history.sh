#!/bin/bash

echo "Git 히스토리에서 대용량 파일 제거 시작합니다..."

# rag-env 전체 제거
git filter-repo --force --path rag-env --invert-paths

# project_db 전체 제거
git filter-repo --force --path project_db --invert-paths

# faiss 인덱스 제거
git filter-repo --force --path-glob "*.faiss" --invert-paths
git filter-repo --force --path-glob "*.pkl" --invert-paths
git filter-repo --force --path-glob "*/faiss_index/*" --invert-paths
git filter-repo --force --path-glob "*/rag_faiss_index/*" --invert-paths

# bitsandbytes / torch 라이브러리 제거
git filter-repo --force --path-glob "*/bitsandbytes/*" --invert-paths
git filter-repo --force --path-glob "*/torch/lib/*" --invert-paths

echo "🧹 Git GC 실행"
git gc --prune=now --aggressive

echo "정리 완료! 저장소 크기:"
du -sh .git