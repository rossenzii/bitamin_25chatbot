from transformers import pipeline, AutoTokenizer
from langchain_huggingface import HuggingFacePipeline
from langchain_core.documents import Document
from typing import List, Dict, Any
from retrievers.hybrid_retriever import get_hybrid_retriever
from prompts.q_prompts import question_prompt

### hybrid_qa_chain: 전체 qa 시스템 조립 (llm 준비: phi-2 모델 로드 + pipeline 생성)

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
    model_id = "skt/kogpt2-base-v2"  # 한국어 GPT-2 (기본 모델, QA에 한계)
    # 토크나이저 로드: text -> token id 변환, token id -> text 복원, 특수 토큰 처리
    tokenizer = AutoTokenizer.from_pretrained(model_id) 
    # pad 토큰 설정 (일부 모델은 기본 Pad 토큰이 없어서 eos 토큰을 pad로 재사용)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id

    pipe = pipeline(
        "text-generation",        # 작업 유형 (huggingface pipeline 유형)
        model=model_id,           # 모델
        device="cpu",             # 실행 디바이스
        trust_remote_code=True,   # 커스텀 모델 코드 허용
        torch_dtype="float32",    # 데이터 타입 (float32로 설정)
        do_sample=False,          # 결정적 생성 (더 일관된 출력)
        max_new_tokens=100,       # 새로 생성할 최대 생성 토큰 수
        pad_token_id=tokenizer.eos_token_id,  # EOS 토큰으로 패딩
        return_full_text=False,   # 입력 텍스트 제외
        tokenizer=tokenizer,      # 토크나이저
        eos_token_id=tokenizer.eos_token_id,  # EOS 토큰 명시
        repetition_penalty=1.5,   # 반복 방지 강화 (질문 반복 방지)
    )
    # hugging face pipeline을 Langchain llm interface로 변환
    llm = HuggingFacePipeline(pipeline=pipe) 

    retriever = get_hybrid_retriever(query)
    
    qa_chain = HybridQAChain(llm, retriever, question_prompt)
    
    return qa_chain