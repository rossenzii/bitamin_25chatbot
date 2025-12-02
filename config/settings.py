"""
프로젝트 루트의 config.settings
각 서브모듈에서 fallback으로 사용됨
"""
import os
from pathlib import Path

# 프로젝트 루트의 .env 파일 찾기
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
env_path = project_root / '.env'

# .env 파일이 있으면 수동으로 읽기 (권한 문제 우회)
if env_path.exists():
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    except (PermissionError, OSError):
        # 권한 문제가 있으면 무시
        pass

# 환경 변수에서 API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 기본 경로 설정
BASE_DIR = str(project_root)
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "rag_faiss_index")
DATA_DIR_PATH = [
    os.path.join(BASE_DIR, "project_txt", "1415V"),
    os.path.join(BASE_DIR, "project_txt", "1415S")
]

