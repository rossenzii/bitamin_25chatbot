import sys, os
sys.path.append(os.path.dirname(__file__))
try:
    from chains.hybrid_qa_chain_openai import create_hybrid_qa_chain
except Exception as e:
    from chains.hybrid_qa_chain import create_hybrid_qa_chain
import traceback

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

def main():
    query = "비타민 홍익대학교 학생은 몇명이야?"
    print(f"질문: {query}\n")
    
    try:
        qa_chain = create_hybrid_qa_chain(query=query)
        result = qa_chain.invoke({"query": query})
        
        print("답변:")
        answer = result.get("result", "")
        print(answer)
        
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
