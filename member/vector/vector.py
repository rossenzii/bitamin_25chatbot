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
retriever = vectorstore.as_retriever(
    search_type="mmr",  # 다양한 문서 조각을 가져오도록
    search_kwargs={"k": 8, "fetch_k": 20}
)

# === 4. 맞춤 프롬프트 정의 ===
# 각 문서별 요약 단계
question_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
아래 문서를 참고하여 질문에 대한 관련된 정보를 요약해 주세요.

질문: {question}
문서: {context}

요약:
"""
)

# 최종 통합 단계
combine_prompt = PromptTemplate(
    input_variables=["question", "summaries"],
    template="""
다음은 여러 문서에서 요약된 내용들입니다. 이를 종합해서 최종 답변을 작성하세요.

질문: {question}
요약들: {summaries}

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
query = "비타민 OT에 대해 알려줘"
answer = qa.invoke({"query": query})
print("최종 답변:", answer["result"])