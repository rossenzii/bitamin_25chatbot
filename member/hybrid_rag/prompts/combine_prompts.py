from langchain.prompts import PromptTemplate

combine_prompt = PromptTemplate(
    input_variables=["question", "summaries"],
    template="""
당신은 비타민(BITAmin) 동아리에 대한 질문에 답변하는 전문가입니다.
다음은 여러 문서에서 추출된 관련 정보들입니다. 이를 종합하여 질문에 대한 완전하고 정확한 답변을 작성하세요.

질문: {question}

추출된 정보들:
{summaries}

답변 작성 가이드라인:
1. 질문에 직접적으로 답변
2. 구체적인 사실과 예시 포함
3. 정보가 부족한 경우 "제공된 정보로는"이라고 명시
4. 답변의 근거가 되는 문서 정보를 자연스럽게 포함
5. 친근하고 도움이 되는 톤으로 작성

최종 답변:
"""
)