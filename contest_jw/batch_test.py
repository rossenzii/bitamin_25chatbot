# ========================================
# 셀 15: 배치 테스트
# ========================================
print("=" * 70)
print("배치 테스트")
print("=" * 70)

def run_batch_test(queries: list):
    """
    여러 질문을 배치로 테스트
    
    Args:
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
        
        result = run_qa_test(query, verbose=True)
        results.append(result)
        
        print(f"\n{'='*70}")
    
    # 요약
    print("\n" + "="*70)
    print(" 배치 테스트 결과 요약")
    print("="*70)
    
    success_count = sum(1 for r in results if r['success'])
    fail_count = len(results) - success_count
    
    print(f"\n 성공: {success_count}개")
    print(f" 실패: {fail_count}개")
    
    if fail_count > 0:
        print(f"\n실패한 질문:")
        for r in results:
            if not r['success']:
                print(f"   - {r['query']}: {r['error']}")
    
    print("\n" + "="*70)
    
    return results

# ========================================
# 테스트 질문 세트
# ========================================

# 다양한 유형의 질문
test_queries = [
    # 공모전
    "동아리 내 chatbot을 rag로 구현하는 프로젝트를 부원들과 함께 진행중인데 이와 관련된 현재 접수중인 공모전 있으면 추천해줄래?",
    
    # 강의
    "머신러닝 기초를 다지기에 좋은 강의 추천 부탁해",
    
    # 혼합
    "딥러닝을 배우고 싶은데 관련 강의와 나갈만한 공모전 둘다 추천해줄 수 있어?"
]

# 배치 테스트 실행
print("\n 배치 테스트 시작!")
batch_results = run_batch_test(test_queries)