import sys, os
sys.path.append(os.path.dirname(__file__))
from chains.qa_chain import create_hybrid_chain

def main():
    query = "포트폴리오 최적화 및 리스크 평가 프로젝트에서는 어떤 모델을 사용했어?"
    print(f"질문: {query}\n")

    qa_chain = create_hybrid_chain()
    answer = qa_chain.invoke({"question": query})

    print("=== 최종 답변 ===")
    print(answer)

if __name__ == "__main__":
    main()