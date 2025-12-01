from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.settings import OPENAI_API_KEY

def create_condense_question_chain():
    # 질문 재구성
    condense_prompt = ChatPromptTemplate.from_messages([
        ("system", """
            당신은 대화 맥락을 이해하는 AI 비서입니다.
            아래의 [대화 기록]과 [사용자의 현재 질문]이 주어집니다.
            
            사용자의 현재 질문이 대명사(그거, 이 프로젝트, 앞서 말한 것 등)를 포함하거나 문맥이 필요하다면, 
            대화 기록을 참고하여 **누구나 이해할 수 있는 구체적이고 독립적인 질문(Standalone Question)**으로 다시 작성하세요.
            
            만약 질문이 이미 구체적이거나 이전 대화와 관련이 없다면, 질문을 변경하지 말고 그대로 출력하세요.
            답변은 하지 말고 **오직 수정된 질문만** 출력하세요.
        """),
        ("human", """
            [대화 기록]
            {chat_history}
            
            [사용자의 현재 질문]
            {question}
        """)
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)
    condense_chain = condense_prompt | llm | StrOutputParser()
    
    return condense_chain