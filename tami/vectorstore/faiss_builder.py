# vectorstore/faiss_builder.py

from langchain_community.vectorstores import FAISS
from typing import List
from langchain_core.documents import Document


class FAISSBuilder:
    """FAISS 인덱스 생성 및 관리"""
    
    def __init__(self, embeddings):
        """
        Args:
            embeddings: 임베딩 모델
        """
        self.embeddings = embeddings
    
    def build(self, documents: List[Document]):
        """
        FAISS 인덱스 생성
        
        Args:
            documents: Document 리스트
        
        Returns:
            vectorstore: FAISS 벡터스토어
        """
        print("=" * 70)
        print("FAISS 인덱스 생성")
        print("=" * 70)
        
        print(f"\n벡터화할 문서: {len(documents)}개")
        print("벡터 생성 중... (시간이 걸릴 수 있습니다)")
        
        vectorstore = FAISS.from_documents(
            documents,
            self.embeddings
        )
        
        print("=" * 70)
        
        return vectorstore
    
    def save(self, vectorstore, path: str):
        """
        FAISS 인덱스 저장
        
        Args:
            vectorstore: FAISS 벡터스토어
            path: 저장 경로
        """
        print(f"\nFAISS 인덱스 저장 중...")
        vectorstore.save_local(path)
        
        print(f"\nFAISS 인덱스 생성 및 저장 완료!")
        print(f"   경로: {path}")
        print("=" * 70)
    
    def load(self, path: str):
        """
        FAISS 인덱스 로드
        
        Args:
            path: 인덱스 경로
        
        Returns:
            vectorstore: FAISS 벡터스토어
        """
        print("\nFAISS 인덱스 로드 중...")
        
        vectorstore = FAISS.load_local(
            path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        print("FAISS 로드 완료!")
        
        return vectorstore