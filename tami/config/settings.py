# config/settings.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """프로젝트 설정 관리"""
    
    def __init__(self):
        # OpenAI API 키
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # 환경 변수에 설정
        os.environ["OPENAI_API_KEY"] = self.openai_api_key
        
        # FAISS 인덱스 경로
        self.faiss_index_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'faiss_index'
        )
        
        # 데이터 소스 기본 경로
        self.data_sources_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data_sources'
        )
    
    def get_api_key(self):
        """API 키 반환"""
        return self.openai_api_key
    
    def get_faiss_path(self):
        """FAISS 인덱스 경로 반환"""
        return self.faiss_index_path
    
    def get_data_sources_path(self):
        """데이터 소스 경로 반환"""
        return self.data_sources_path