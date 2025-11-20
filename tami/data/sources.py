# data/sources.py

import os

def get_data_sources(base_path):
    """
    데이터 소스 정의
    
    Args:
        base_path: data_sources 폴더 경로
    
    Returns:
        data_sources: 데이터 소스 리스트
    """
    
    data_sources = [
        {
            "path": os.path.join(base_path, "dacon/dacon.json"),
            "type": "competition",
            "platform": "dacon",
            "description": "데이콘 AI 경진대회"
        },
        {
            "path": os.path.join(base_path, "inflearn/inflearn_courses_all.json"),
            "type": "education",
            "platform": "inflearn",
            "description": "인프런 온라인 강의"
        },
        {
            "path": os.path.join(base_path, "lh_compas/lh_compas_산학협력.json"),
            "type": "competition",
            "platform": "lh_compas",
            "description": "LH 컴퍼스 산학협력"
        },
        {
            "path": os.path.join(base_path, "lh_compas/lh_compas_아이디어공모전.json"),
            "type": "competition",
            "platform": "lh_compas",
            "description": "LH 컴퍼스 아이디어 공모전"
        },
        {
            "path": os.path.join(base_path, "kaggle/kaggle_active_korean.json"),
            "type": "competition",
            "platform": "kaggle",
            "description": "Kaggle 경진대회 (한국어)"
        },
        {
            "path": os.path.join(base_path, "linkareer/linkareer.json"),
            "type": "auto",
            "platform": "linkareer",
            "description": "링커리어 (대외활동/공모전 자동 구분)"
        },
        {
            "path": os.path.join(base_path, "공공데이터포털/data_go_kr.json"),
            "type": "competition",
            "platform": "data_go_kr",
            "description": "공공데이터포털 공모전"
        },
    ]
    
    return data_sources