#!/bin/bash
# Streamlit 앱 실행을 위한 의존성 설치 스크립트

echo "=== BITAmin Streamlit 앱 의존성 설치 ==="
echo ""

# 가상환경 확인 및 활성화
if [ -d "rag-env" ]; then
    echo "가상환경 'rag-env' 발견 - 활성화 중..."
    source rag-env/bin/activate
    echo "가상환경 활성화됨"
    echo "Python 경로: $(which python)"
    echo ""
else
    echo "가상환경이 없습니다. 새로 생성할까요? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        python3 -m venv rag-env
        source rag-env/bin/activate
        echo "가상환경 생성 및 활성화됨"
    else
        echo "시스템 Python 사용 (권장하지 않음)"
    fi
    echo ""
fi

# requirements.txt 설치
echo "requirements.txt에서 패키지 설치 중..."
pip install -r requirements.txt

# Streamlit이 가상환경에 설치되어 있는지 확인
echo ""
echo "Streamlit 설치 확인 중..."
if ! command -v streamlit &> /dev/null || [ "$(which streamlit)" != "$(dirname $(which python))/streamlit" ]; then
    echo "Streamlit이 가상환경에 없습니다. 설치 중..."
    pip install streamlit
fi

echo ""
echo "=== 설치 완료 ==="
echo ""
echo "현재 Python: $(which python)"
echo "현재 Streamlit: $(which streamlit)"
echo ""
echo "Streamlit 앱 실행:"
echo "  source rag-env/bin/activate  # 가상환경 활성화"
echo "  streamlit run streamlit_app.py"
echo ""
echo "또는 한 번에:"
echo "  ./run_streamlit.sh"
echo ""
echo "문제가 발생하면 다음을 확인하세요:"
echo "  1. 가상환경이 활성화되어 있는지 (source rag-env/bin/activate)"
echo "  2. .env 파일에 OPENAI_API_KEY가 설정되어 있는지"
echo "  3. 각 카테고리별 FAISS 인덱스가 생성되어 있는지"

