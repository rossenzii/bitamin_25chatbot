from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch
from langchain_core.output_parsers import StrOutputParser
from config.settings import OPENAI_API_KEY

# 질문 유형 분류 체인
def create_question_classifier(llm_model: str = "gpt-4o-mini"):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
당신은 사용자의 질문을 다음 유형 중 하나로 분류하는 역할을 합니다:
- TYPE_1: 전반적인 프로젝트 혹은 대표 프로젝트 설명 요청 (특정 카테고리, 기수/시기가 명시되지 않았을 경우)
        ※예: "비타민의 프로젝트로는 어떤 게 있는지 알려줘", 
            "전체 프로젝트 알려줘", 
            "비타민 프로젝트 개요 알려줘",
            "대표 프로젝트 알려줘"
- TYPE_2: 카테고리별 프로젝트 요약 요청 (NLP, CV, 추천시스템)
- TYPE_3: 특정 기수/시기 프로젝트 요약 요청
- TYPE_4: 특정 프로젝트의 세부 설명 요청 (데이터, 전처리, 모델, 성능 등 구체적인 기술 정보)
        ※예: '이 프로젝트에서 사용한 모델은 무엇이야?', '이 프로젝트는 어떤 데이터를 사용했어?"
- OTHER: 기술 질문 등 RAG 범위를 벗어난 일반 기술 질문

반환은 반드시 한 단어로 TYPE_1, TYPE_2, TYPE_3, TYPE_4, OTHER 중 하나만 사용하세요.
        """),
        ("human", "{question}")
    ])
<<<<<<< HEAD
    llm = ChatOpenAI(model=llm_model, temperature=0, openai_api_key=OPEN_API_KEY)
=======
    llm = ChatOpenAI(model=llm_model, temperature=0, openai_api_key=OPENAI_API_KEY)
>>>>>>> hr
    classifier_chain = prompt | llm | StrOutputParser()
    return classifier_chain

# 질문 유형별 체인 정의
def create_type_chains():
    from prompts.question_prompts import (
        TYPE_1_PROMPT, TYPE_2_PROMPT, TYPE_3_PROMPT, TYPE_4_PROMPT, DEFAULT_PROMPT
    )
<<<<<<< HEAD
    llm_model = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPEN_API_KEY)
=======
    llm_model = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)
>>>>>>> hr

    type_1_chain = TYPE_1_PROMPT | llm_model
    type_2_chain = TYPE_2_PROMPT | llm_model
    type_3_chain = TYPE_3_PROMPT | llm_model
    type_4_chain = TYPE_4_PROMPT | llm_model
    default_chain = DEFAULT_PROMPT | llm_model

    # RunnableBranch 정의
    branch = RunnableBranch(
        (lambda x: x["type"] == "TYPE_1", type_1_chain),
        (lambda x: x["type"] == "TYPE_2", type_2_chain),
        (lambda x: x["type"] == "TYPE_3", type_3_chain),
        (lambda x: x["type"] == "TYPE_4", type_4_chain),
        default_chain
    )

    return branch