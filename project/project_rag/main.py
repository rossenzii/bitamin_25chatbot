import sys, os
sys.path.append(os.path.dirname(__file__))
from chains.qa_chain import create_hybrid_chain

def main():
    query = "국회 회의봇 기반 현안 질의 챗봇 프로젝트에서는 어떤 데이터, 모델을 사용했어?"
    print(f"질문: {query}\n")

    qa_chain = create_hybrid_chain()
    answer = qa_chain.invoke({"question": query})

    print("=== 최종 답변 ===")
    print(answer)

if __name__ == "__main__":
    main()