#!/bin/bash
# Streamlit 앱 실행 스크립트 (가상환경 자동 활성화)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 가상환경 확인 및 활성화
if [ -d "rag-env" ]; then
    echo "가상환경 활성화 중..."
    source rag-env/bin/activate
    echo "가상환경 활성화됨"
    echo "Python: $(which python)"
    echo "Streamlit: $(which streamlit)"
    echo ""
else
    echo "가상환경 'rag-env'를 찾을 수 없습니다."
    echo "먼저 ./install_dependencies.sh를 실행하세요."
    exit 1
fi

# Streamlit 실행
echo "Streamlit 앱 시작 중..."
echo ""
streamlit run streamlit_app.py

