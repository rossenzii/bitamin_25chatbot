# ========================================
# 셀 13: QA Chain 
# ========================================
print("=" * 70)
print("QA Chain 구현 (URL 할루시네이션 완전 방지)")
print("=" * 70)

import os
import re
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

def fix_urls_in_answer_v2(answer: str, docs: list) -> str:
    """
    LLM 답변의 잘못된 URL을 실제 문서 URL로 강제 교체 (강화 버전)
    
    전략:
    1. 답변에서 "추천 목록" 섹션 찾기
    2. 각 항목의 제목 추출
    3. 제목으로 실제 문서 찾기
    4. 실제 URL로 강제 교체
    """
    
    # 1. 문서별 제목-URL 매핑 생성
    title_to_doc = {}
    for doc in docs:
        title = doc.metadata.get('title', '').strip()
        if title:
            normalized = title.lower().replace(' ', '')
            title_to_doc[normalized] = doc
    
    # 2. 답변에서 목록 부분 찾기
    list_pattern = r'\*\*추천.*?목록\*\*\s*\n+(.*?)(?=\n\n|$)'
    list_match = re.search(list_pattern, answer, re.DOTALL)
    
    if not list_match:
        return answer
    
    list_section = list_match.group(1)
    new_list_items = []
    
    # 3. 각 항목 처리
    item_pattern = r'(\d+)\.\s*([^\n]+)\n\s*(.+?)(?=\n\d+\.|$)'
    
    for match in re.finditer(item_pattern, list_section, re.DOTALL):
        number = match.group(1)
        title = match.group(2).strip()
        old_url = match.group(3).strip()
        
        normalized_title = title.lower().replace(' ', '')
        
        correct_url = None
        best_match_doc = None
        best_score = 0
        
        for norm_key, doc in title_to_doc.items():
            if normalized_title in norm_key or norm_key in normalized_title:
                score = len(set(normalized_title) & set(norm_key))
                if score > best_score:
                    best_score = score
                    best_match_doc = doc
        
        if best_match_doc:
            correct_url = best_match_doc.metadata.get('url', '')
        
        if correct_url and correct_url not in ['Unknown', None, '', '해당없음']:
            if not correct_url.startswith('http'):
                correct_url = f"https://{correct_url}"
            new_item = f"{number}. {title}\n   {correct_url}"
        else:
            print(f"   URL 없음 (제외): {title[:30]}...")
            continue
        
        new_list_items.append(new_item)
    
    if new_list_items:
        new_list_section = '\n\n'.join(new_list_items)
        fixed_answer = answer[:list_match.start(1)] + new_list_section + answer[list_match.end(1):]
        return fixed_answer
    
    return answer

def create_hybrid_qa_chain(query: str = None):
    """URL 할루시네이션 완전 방지 QA Chain"""
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=OPENAI_API_KEY,
        temperature=0.7,
        max_tokens=1000,
    )
    
    # Retriever (4개 값 받기!)
    if query:
        retriever, topic, weights, search_filter = get_hybrid_retriever(query)
        print(f"Retriever: {topic} (BM25={weights[0]}, Vector={weights[1]})")
    else:
        retriever, topic, weights, search_filter = get_hybrid_retriever()
    
    # Custom QA Chain
    class URLFixedQAChain:
        def __init__(self, llm, retriever, prompt):
            self.llm = llm
            self.retriever = retriever
            self.prompt = prompt
        
        def invoke(self, inputs):
            query = inputs['query']
            
            # 1. 문서 검색
            docs = self.retriever.get_relevant_documents(query)
            
            print(f"\n검색된 문서: {len(docs)}개")
            for i, doc in enumerate(docs[:5], 1):
                title = doc.metadata.get('title', '')[:40]
                url = doc.metadata.get('url', '')[:60]
                print(f"   [{i}] {title}...")
                print(f"       URL: {url}...")
            
            # 2. 컨텍스트 생성
            context_parts = []
            for i, doc in enumerate(docs, 1):
                title = doc.metadata.get('title', 'Unknown')
                doc_type = doc.metadata.get('type', 'Unknown')
                platform = doc.metadata.get('platform', '')
                url = doc.metadata.get('url', '')
                content = doc.page_content
                
                context = f"\n--- 문서 {i} ---\n"
                context += f"제목: {title}\n"
                context += f"유형: {doc_type}\n"
                
                if platform and platform not in ['Unknown', None, '', '해당없음']:
                    context += f"플랫폼: {platform}\n"
                
                if url and url not in ['Unknown', None, '', '해당없음']:
                    context += f"URL: {url}\n"
                
                context += f"\n내용:\n{content}\n"
                context_parts.append(context)
            
            context = "\n".join(context_parts)
            
            # 3. 프롬프트 생성
            formatted_prompt = self.prompt.format(
                context=context,
                question=query
            )
            
            # 4. LLM 호출
            print("\nLLM 답변 생성 중...")
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            raw_answer = response.content
            
            print("LLM 답변 생성 완료")
            
            # 5. URL 후처리
            print("\nURL 검증 및 교체 중...")
            fixed_answer = fix_urls_in_answer_v2(raw_answer, docs)
            print("URL 교체 완료")
            
            return {
                'result': fixed_answer,
                'source_documents': docs,
                'raw_result': raw_answer
            }
    
    qa_chain = URLFixedQAChain(llm, retriever, question_prompt)
    
    return qa_chain

print("URL 할루시네이션 방지 QA Chain 준비 완료!")
print("=" * 70)