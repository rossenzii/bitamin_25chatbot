from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
            당신은 비타민(BITAmin) 동아리에서 진행한 프로젝트 관리 전문가입니다.
            주어진 문서들(Context)에서 사용자의 질문에 관련된 프로젝트 정보를 정확하게 추출하여 답변해주세요.

            질문: {question}

            문서 내용: {context}

            요구사항:
            1. 질문과 관련이 있는 프로젝트만 선별해주세요.
            3. 질문과 관련된 프로젝트를 최대 3개까지 선택해 답변해주세요.
            4. 각 프로젝트별로 이름과 프로젝트 전반에 걸친 핵심 요약을 함께 제시하세요.
            5. 반드시 프로젝트 이름을 그대로 포함하세요.
            6. 질문이 특정 프로젝트를 묻는 것이 아니라면, 3가지 프로젝트를 선택해 각 프로젝트의 이름과 프로젝트 전반에 걸친 핵심 내용을 요약하여 답변해주세요.

            답변:
            """
)