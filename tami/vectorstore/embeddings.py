# vectorstore/embeddings.py

import os
from langchain_openai import OpenAIEmbeddings


class EmbeddingManager:
    """임베딩 모델 관리"""
    
    def __init__(self, api_key: str):
        """
        Args:
            api_key: OpenAI API 키
        """
        print("=" * 70)
        print("OpenAI 임베딩 모델 로드")
        print("=" * 70)
        
        print("\nOpenAI 임베딩 모델 로드 중...")
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key
        )
        
        print("OpenAI 임베딩 모델 로드 완료!")
        
        # 테스트
        print("\n임베딩 테스트 중...")
        test_vector = self.embeddings.embed_query("테스트 문장입니다")
        print(f"벡터 차원: {len(test_vector)}차원")
        print(f"   (text-embedding-3-small: 1536차원)")
        
        print("=" * 70)
    
    def get_embeddings(self):
        """임베딩 모델 반환"""
        return self.embeddings