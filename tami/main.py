# main.py

import traceback
from config import Config
from data import get_data_sources
from utils import create_all_documents, remove_duplicates
from vectorstore import EmbeddingManager, FAISSBuilder
from retriever import HybridRetriever
from prompts import create_qa_prompt
from chains import create_hybrid_qa_chain


def run_qa_test(qa_chain, query: str, verbose: bool = True):
    """
    QA 실행 함수
    
    Args:
        qa_chain: QA Chain 객체
        query: 사용자 질문
        verbose: 상세 출력 여부
    
    Returns:
        result: 실행 결과 딕셔너리
    """
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"질문: {query}")
        print('='*70)
    
    try:
        # 답변 생성
        result = qa_chain.invoke({"query": query})
        
        # 답변 출력
        answer = result.get("result", "답변을 생성하지 못했습니다.")
        
        if verbose:
            print("\n답변:")
            print("-" * 70)
            print(answer)
            print("-" * 70)
            
            # 참조 문서 정보
            source_docs = result.get("source_documents", [])
            if source_docs:
                print(f"\n참조 문서 ({len(source_docs)}개):")
                for i, doc in enumerate(source_docs[:5], 1):
                    title = doc.metadata.get('title', 'Unknown')
                    doc_type = doc.metadata.get('type', 'Unknown')
                    platform = doc.metadata.get('platform', 'Unknown')
                    
                    print(f"\n   [{i}] {title}")
                    print(f"       유형: {doc_type} | 플랫폼: {platform}")
                    
                    url = doc.metadata.get('url', '')
                    if url:
                        print(f"       {url}")
        
        return {
            'success': True,
            'query': query,
            'answer': answer,
            'source_documents': result.get("source_documents", []),
            'error': None
        }
        
    except Exception as e:
        if verbose:
            print(f"\n오류 발생: {str(e)}")
            traceback.print_exc()
        
        return {
            'success': False,
            'query': query,
            'answer': None,
            'source_documents': [],
            'error': str(e)
        }


def run_batch_test(qa_chain, queries: list):
    """
    여러 질문을 배치로 테스트
    
    Args:
        qa_chain: QA Chain 객체
        queries: 질문 리스트
    
    Returns:
        results: 결과 리스트
    """
    
    print(f"\n총 {len(queries)}개 질문 테스트 시작\n")
    
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/{len(queries)}] 테스트 진행 중...")
        print('='*70)
        
        result = run_qa_test(qa_chain, query, verbose=True)
        results.append(result)
        
        print(f"\n{'='*70}")
    
    # 요약
    print("\n" + "="*70)
    print("배치 테스트 결과 요약")
    print("="*70)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"\n성공: {success_count}개")
    print(f"실패: {fail_count}개")
    
    if fail_count > 0:
        print(f"\n실패한 질문:")
        for r in results:
            if not r['success']:
                print(f"   - {r['query']}: {r['error']}")
    
    print("\n" + "="*70)
    
    return results


def main():
    """메인 실행 함수"""
    
    print("=" * 70)
    print("비타민 RAG 챗봇 시작")
    print("=" * 70)
    
    # 1. 설정 로드
    config = Config()
    api_key = config.get_api_key()
    
    # 2. 데이터 소스 정의
    print("\n" + "=" * 70)
    print("데이터 소스 정의")
    print("=" * 70)
    data_sources = get_data_sources(config.get_data_sources_path())
    print(f"\n총 {len(data_sources)}개 데이터 소스")
    for i, source in enumerate(data_sources, 1):
        print(f"  [{i}] {source['platform']:15s} - {source['description']}")
    print("=" * 70)
    
    # 3. Document 생성
    print("\n" + "=" * 70)
    print("Document 생성 시작")
    print("=" * 70)
    documents = create_all_documents(data_sources)
    print(f"\n총 {len(documents)}개 Document 생성 완료!")
    print("=" * 70)
    
    # 4. 중복 제거
    documents = remove_duplicates(documents)
    
    # 5. 임베딩 준비
    emb_manager = EmbeddingManager(api_key)
    embeddings = emb_manager.get_embeddings()
    
    # 통계
    print(f"\n통계:")
    print(f"   총 문서: {len(documents):,}개")
    lengths = [len(doc.page_content) for doc in documents[:100]]
    avg_length = sum(lengths) / len(lengths) if lengths else 0
    print(f"   평균 길이: {avg_length:.0f}자")
    print(f"\n공모전/강의 데이터는 이미 짧아서 Chunking을 생략합니다.")
    print("   (Chunking은 긴 문서에만 필요합니다)")
    print("=" * 70)
    
    # 6. FAISS 인덱스 생성
    builder = FAISSBuilder(embeddings)
    vectorstore = builder.build(documents)
    builder.save(vectorstore, config.get_faiss_path())
    
    # 7. Hybrid Retriever 생성
    retriever = HybridRetriever(vectorstore, documents)
    
    # 8. 프롬프트 생성
    prompt = create_qa_prompt()
    
    # 9. QA Chain 생성
    qa_chain = create_hybrid_qa_chain(api_key, retriever, prompt)
    
    # 10. 테스트 실행
    print("\n" + "=" * 70)
    print("단일 테스트 실행")
    print("=" * 70)
    
    test_query = "llm 관련해서 공모전이나 강의 추천해줄래?"
    result = run_qa_test(qa_chain, test_query, verbose=True)
    
    print("\n" + "=" * 70)
    
    # 11. 배치 테스트 (옵션)
    # test_queries = [
    #     "동아리 내 chatbot을 rag로 구현하는 프로젝트를 부원들과 함께 진행중인데 이와 관련된 현재 접수중인 공모전 있으면 추천해줄래?",
    #     "머신러닝 기초를 다지기에 좋은 강의 추천 부탁해",
    #     "딥러닝을 배우고 싶은데 관련 강의와 나갈만한 공모전 둘다 추천해줄 수 있어?"
    # ]
    # batch_results = run_batch_test(qa_chain, test_queries)


if __name__ == "__main__":
    main()