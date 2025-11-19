from dotenv import load_dotenv
import os

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# === 1. 벡터 DB 불러오기 ===
embeddings = OpenAIEmbeddings(openai_api_key=api_key)
vectorstore = FAISS.load_local(
    "./rag_faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
print("벡터 DB 로드 완료")

# === 2. LLM 준비 ===
llm = ChatOpenAI(
    model="gpt-4o-mini", 
    openai_api_key=api_key,
    temperature=0.2
)

# === 3. Retriever 세팅 (MMR 활용) ===
def filter_documents(docs, query):
    """질문과 관련성이 높은 문서만 필터링"""
    filtered_docs = []
    query_lower = query.lower()

    for doc in docs:
        content = doc.page_content.lower()
        metadata = doc.metadata.get('type', '')

        # 멤버 관련
        if any(word in query_lower for word in ['멤버', '회원', '구성원']) and metadata == 'member':
            filtered_docs.append(doc)

        # 커리큘럼 관련
        elif any(word in query_lower for word in ['커리큘럼', '강의', '세션', '스터디']) and metadata in [
            'regular_session', 'annual_session', 'study', 'lecture'
        ]:
            filtered_docs.append(doc)

        # 비타민 정보 관련 (모집, 문의, 수상 내역, 활동 등)
        elif any(word in query_lower for word in ['모집', '문의', '수상', '세션', '스터디', '프로젝트', '컨퍼런스', '데이터톤', 'mt', '소모임', '비타민']):
            if metadata in ['schedule', 'contact', 'award', 'activity', 'conference', 'datathon']:
                filtered_docs.append(doc)

        # 그 외: 질의어에 포함된 단어가 문서 내용에 있으면 필터링
        elif any(keyword in content for keyword in query_lower.split()):
            filtered_docs.append(doc)

    return filtered_docs[:5]  # 최대 5개만 

retriever = vectorstore.as_retriever(
    search_type="mmr",  # 다양한 문서 조각을 가져오도록
    search_kwargs={"k": 8, "fetch_k": 20, "lambda_mult": 0.7}  # 더 많은 후보에서 선택
)

# === 4. 맞춤 프롬프트 정의 ===
# 각 문서별 요약 단계
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

# 최종 통합 단계
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

# === 5. Retrieval QA 체인 만들기 (map_reduce 방식) ===
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="map_reduce",
    chain_type_kwargs={
        "question_prompt": question_prompt,
        "combine_prompt": combine_prompt
    }
)

# === 6. 질의 & 답변 ===
query = "비타민 동아리의 MT 활동에 대해 설명해주세요"

# TEST: 검색된 문서들 확인
print("=== 원본 검색된 문서들 ===")
raw_docs = retriever.get_relevant_documents(query)
for i, doc in enumerate(raw_docs):
    print(f"\n문서 {i+1}:")
    print(f"내용: {doc.page_content}")
    print(f"메타데이터: {doc.metadata}")

# 
print("\n=== 필터링된 문서들 ===")
filtered_docs = filter_documents(raw_docs, query)
for i, doc in enumerate(filtered_docs):
    print(f"\n문서 {i+1}:")
    print(f"내용: {doc.page_content}")
    print(f"메타데이터: {doc.metadata}")


# 최종 답변
print("\n=== 최종 답변 ===")
answer = qa.invoke({"query": query})
print("최종 답변:", answer["result"])