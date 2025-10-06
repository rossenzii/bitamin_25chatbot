from langchain.prompts import PromptTemplate

question_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
당신은 비타민(BITAmin) 동아리에 대한 질문에 답변하는 전문가입니다.
주어진 문서에서 질문과 관련된 정보만을 정확히 추출하여 요약해주세요.

질문: {question}

문서 내용:
{context}

요구사항:
1. 질문과 직접적으로 관련된 정보만 추출
2. 구체적인 사실과 데이터를 포함
3. 불확실한 정보는 포함하지 않음
4. 간결하고 명확하게 작성

관련 정보 요약:
"""
)