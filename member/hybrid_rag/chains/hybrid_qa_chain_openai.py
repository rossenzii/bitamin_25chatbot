import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from typing import List, Dict, Any

# 환경 변수 우선 사용 (배포 환경 대응)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# config import 시도 (선택사항)
if not OPENAI_API_KEY:
    try:
        from member.hybrid_rag.config.settings import OPENAI_API_KEY as CONFIG_KEY
        OPENAI_API_KEY = CONFIG_KEY
    except ImportError:
        try:
            from config.settings import OPENAI_API_KEY as CONFIG_KEY
            OPENAI_API_KEY = CONFIG_KEY
        except ImportError:
            pass

# 모듈 import
try:
    from member.hybrid_rag.retrievers.hybrid_retriever import get_hybrid_retriever
    from member.hybrid_rag.prompts.q_prompts import question_prompt
except ImportError:
    from retrievers.hybrid_retriever import get_hybrid_retriever
    from prompts.q_prompts import question_prompt

### hybrid_qa_chain: OpenAI API를 사용하는 버전 (더 나은 한국어 답변)

class HybridQAChain:
    def __init__(self, llm, retriever, prompt):
        self.llm = llm
        self.retriever = retriever
        self.prompt = prompt
    
    def invoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs['query']
        
        # 1. 문서 검색
        docs = self.retriever.get_relevant_documents(query)
        
        # 2. 컨텍스트 생성
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 3. 프롬프트 생성
        formatted_prompt = self.prompt.format(
            context=context,
            question=query
        )
        
        # 4. LLM 호출
        response = self.llm.invoke(formatted_prompt)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        return {
            'result': answer,
            'source_documents': docs
        }

def create_hybrid_qa_chain(query=None):
    # OpenAI API 사용 (한국어 처리 우수, QA 태스크 최적화)
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # 빠르고 저렴한 모델
        openai_api_key=OPENAI_API_KEY,
        temperature=0.2,  # 일관된 답변
    )
    retriever = get_hybrid_retriever(query)
    
    qa_chain = HybridQAChain(llm, retriever, question_prompt)
    
    return qa_chain

