import sys, os
sys.path.append(os.path.dirname(__file__))
from chains.qa_chain import create_hybrid_chain

def format_chat_history(history):
    return "\n".join([f"User: {h[0]}\nAI: {h[1]}" for h in history])

def main():
    print("종료: q")
    
    qa_chain = create_hybrid_chain()
    
    chat_history = [] 

    while True:
        query = input("\n질문: ")
        if query.lower() in ["q", "exit", "quit"]:
            break

        history_str = format_chat_history(chat_history)

        print("생각 중...", end="", flush=True)
        result = qa_chain.invoke({
            "question": query, 
            "chat_history": history_str
        })
        
        print(f"\r=== 답변 ===\n{result}")
        
        # 대화 기록 업데이트
        chat_history.append((query, result))

if __name__ == "__main__":
    main()