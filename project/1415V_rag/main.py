import sys, os
sys.path.append(os.path.dirname(__file__))
from chains.qa_chain import create_hybrid_chain

def main():
    query = "비타민에서 진행했던 프로젝트에 대해 설명해주세요"
    print(f"질문: {query}\n")

    qa_chain = create_hybrid_chain(query=query)
    answer = qa_chain.invoke({"query": query})

    print("=== 최종 답변 ===")
    print(answer["result"])

if __name__ == "__main__":
    main()