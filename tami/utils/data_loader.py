# utils/data_loader.py

import json

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