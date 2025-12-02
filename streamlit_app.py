import streamlit as st
import sys
import os
from datetime import datetime
from pathlib import Path

# OpenMP 충돌 방지 (반드시 다른 import 전에 설정)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# 프로젝트 루트 경로 추가
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

# 환경 변수 로드 (로컬 환경)
from dotenv import load_dotenv
import os

# Streamlit Cloud secrets 또는 .env 파일에서 환경 변수 로드
load_dotenv()
# Streamlit Cloud 환경 설정
# Streamlit secrets 또는 환경 변수에서 API 키 로드
try:
    # Streamlit Cloud에서 secrets 사용
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
        if 'HUGGINGFACEHUB_API_TOKEN' in st.secrets:
            os.environ['HUGGINGFACEHUB_API_TOKEN'] = st.secrets['HUGGINGFACEHUB_API_TOKEN']
except Exception:
    pass

# 환경 변수가 없으면 .env에서 로드 시도
if not os.environ.get('OPENAI_API_KEY'):
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key == 'OPENAI_API_KEY':
                            os.environ['OPENAI_API_KEY'] = value
                        elif key == 'HUGGINGFACEHUB_API_TOKEN':
                            os.environ['HUGGINGFACEHUB_API_TOKEN'] = value
        except Exception:
            pass

# 페이지 설정
st.set_page_config(
    page_title="BITAmin - AI Assistant",
    page_icon="bitamin-favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FF6B35 0%, #2C2C2C 100%) !important;
        min-width: 250px;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    [data-testid="stSidebar"] button {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: none !important;
        margin: 0.25rem 0.5rem !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    [data-testid="stSidebar"] button[kind="primary"] {
        background-color: rgba(255, 255, 255, 0.3) !important;
        font-weight: bold !important;
    }
    
    /* 카테고리 헤더 */
    .category-header {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: bold;
        padding: 1rem 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* 카테고리 아이템 */
    .category-item {
        padding: 0.75rem 1.5rem;
        color: #FFFFFF;
        cursor: pointer;
        transition: all 0.3s;
        border-radius: 8px;
        margin: 0.25rem 0.5rem;
    }
    
    .category-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .category-item.active {
        background-color: rgba(255, 255, 255, 0.2);
        font-weight: bold;
    }
    
    .category-item.inactive {
        color: #CCCCCC;
    }
    
    /* 서브메뉴 */
    .submenu-item {
        padding: 0.5rem 1.5rem 0.5rem 3rem;
        color: #FFFFFF;
        font-size: 14px;
    }
    
    /* 메인 영역 */
    .main-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem;
        border-bottom: 1px solid #E0E0E0;
    }
    
    .logo-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 24px;
    }
    
    /* 채팅 메시지 스타일 */
    .chat-message {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .chat-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .chat-avatar.user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .chat-avatar.assistant {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
    }
    
    .chat-bubble {
        background: #F5F5F5;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .chat-bubble.user {
        background: #E3F2FD;
        margin-left: auto;
    }
    
    .chat-timestamp {
        font-size: 12px;
        color: #999;
        margin-top: 0.5rem;
    }
    
    /* 입력 영역 */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #E0E0E0;
        z-index: 100;
    }
    
    /* 스크롤 영역 */
    .chat-container {
        padding-bottom: 100px;
    }
    
    /* 하단 아이콘 */
    .bottom-icon {
        position: absolute;
        bottom: 1rem;
        left: 1rem;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = {}
    
if "current_category" not in st.session_state:
    st.session_state.current_category = "멤버"

if "qa_chains" not in st.session_state:
    st.session_state.qa_chains = {}

# 카테고리별 초기 메시지
initial_messages = {
    "멤버": "안녕하세요! 비타민 챗봇 타미입니다. 비타민 멤버에 대해 무엇이든지 물어보세요!",
    "활동": "안녕하세요! 비타민 챗봇 타미입니다. 대외 활동, 공모전, 강의에 대해 무엇이든지 물어보세요!",
    "프로젝트": "안녕하세요! 비타민 챗봇 타미입니다. 비타민 프로젝트에 대해 무엇이든지 물어보세요!"
}

# 각 카테고리별 메시지 초기화
for category in ["멤버", "활동", "프로젝트"]:
    if category not in st.session_state.messages:
        st.session_state.messages[category] = [
            {
                "role": "assistant",
                "content": initial_messages[category],
                "timestamp": datetime.now().strftime("%I:%M %p")
            }
        ]

# 사이드바
with st.sidebar:
    st.markdown('<div class="category-header">카테고리</div>', unsafe_allow_html=True)
    
    # 멤버 섹션
    if st.button("멤버", key="btn_member", use_container_width=True, 
                 type="primary" if st.session_state.current_category == "멤버" else "secondary"):
        st.session_state.current_category = "멤버"
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 활동 섹션
    if st.button("활동", key="btn_activity", use_container_width=True,
                 type="primary" if st.session_state.current_category == "활동" else "secondary"):
        st.session_state.current_category = "활동"
        st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 프로젝트 섹션
    if st.button("프로젝트", key="btn_project", use_container_width=True,
                 type="primary" if st.session_state.current_category == "프로젝트" else "secondary"):
        st.session_state.current_category = "프로젝트"
        st.rerun()
    

# 메인 영역
st.markdown("""
<div class="main-header">
    <div class="logo-circle">B</div>
    <div>
        <h1 style="margin: 0; font-size: 28px;">BITAmin</h1>
        <p style="margin: 0; color: #666; font-size: 14px;">AI Assistant</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 채팅 메시지 표시
current_messages = st.session_state.messages.get(st.session_state.current_category, [])

# 채팅 컨테이너
chat_container = st.container()
with chat_container:
    for msg in current_messages:
        role = msg["role"]
        content = msg["content"]
        timestamp = msg.get("timestamp", "")
        
        avatar_class = "user" if role == "user" else "assistant"
        avatar_text = "U" if role == "user" else "A"
        bubble_class = "user" if role == "user" else ""
        
        st.markdown(f"""
        <div class="chat-message">
            <div class="chat-avatar {avatar_class}">{avatar_text}</div>
            <div class="chat-bubble {bubble_class}">
                {content}
                <div class="chat-timestamp">{timestamp}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 입력 영역
col1, col2 = st.columns([6, 1])

with col1:
    user_input = st.text_input(
        "Type your message...",
        key="user_input",
        label_visibility="collapsed",
        placeholder="Type your message..."
    )

with col2:
    send_button = st.button("Send", type="primary", use_container_width=True)

# 질문 처리
if send_button and user_input:
    category = st.session_state.current_category
    current_messages = st.session_state.messages.get(category, [])
    
    # 사용자 메시지 추가
    current_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%I:%M %p")
    })
    st.session_state.messages[category] = current_messages
    
    # 답변 생성
    try:
        if category == "멤버":
            try:
                from member.hybrid_rag.chains.hybrid_qa_chain_openai import create_hybrid_qa_chain
            except ImportError as e:
                error_msg = f"모듈 import 오류: {str(e)}\n\n필요한 패키지를 설치해주세요:\npip install langchain-openai langchain-community langchain-core"
                current_messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.messages[category] = current_messages
                st.rerun()
                st.stop()
            
            with st.spinner("답변을 생성하고 있습니다..."):
                if category not in st.session_state.qa_chains:
                    print(f"[DEBUG] {category} 체인 생성 중...")
                    st.session_state.qa_chains[category] = create_hybrid_qa_chain(query=user_input)
                    print(f"[DEBUG] {category} 체인 생성 완료")
                
                qa_chain = st.session_state.qa_chains[category]
                print(f"[DEBUG] 질문 처리 시작: {user_input[:50]}...")
                result = qa_chain.invoke({"query": user_input})
                print(f"[DEBUG] 질문 처리 완료")
                answer = result.get("result", "답변을 생성하지 못했습니다.")
            
        elif category == "활동":
            try:
                from contest_jw.chains.qa_chain import create_hybrid_qa_chain
            except ImportError as e:
                error_msg = f"모듈 import 오류: {str(e)}\n\n필요한 패키지를 설치해주세요:\npip install langchain-openai langchain-community langchain-core"
                current_messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.messages[category] = current_messages
                st.rerun()
                st.stop()
            
            with st.spinner("🤔 답변을 생성하고 있습니다..."):
                if category not in st.session_state.qa_chains:
                    print(f"[DEBUG] {category} 체인 생성 중...")
                    st.session_state.qa_chains[category] = create_hybrid_qa_chain(query=user_input)
                    print(f"[DEBUG] {category} 체인 생성 완료")
                
                qa_chain = st.session_state.qa_chains[category]
                print(f"[DEBUG] 질문 처리 시작: {user_input[:50]}...")
                result = qa_chain.invoke({"query": user_input})
                print(f"[DEBUG] 질문 처리 완료")
                answer = result.get("result", "답변을 생성하지 못했습니다.")
            
        elif category == "프로젝트":
            try:
                from project.project_rag.chains.qa_chain import create_hybrid_chain
            except ImportError as e:
                error_msg = f"모듈 import 오류: {str(e)}\n\n필요한 패키지를 설치해주세요:\npip install langchain-openai langchain-community langchain-core"
                current_messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                st.session_state.messages[category] = current_messages
                st.rerun()
                st.stop()
        
            with st.spinner("답변을 생성하고 있습니다..."):
                if category not in st.session_state.qa_chains:
                    print(f"[DEBUG] {category} 체인 생성 중...")
                    st.session_state.qa_chains[category] = create_hybrid_chain()
                    print(f"[DEBUG] {category} 체인 생성 완료")
                
                qa_chain = st.session_state.qa_chains[category]
                print(f"[DEBUG] 질문 처리 시작: {user_input[:50]}...")
                result = qa_chain.invoke({"question": user_input})
                print(f"[DEBUG] 질문 처리 완료")
                answer = result if isinstance(result, str) else str(result)
        
        # 어시스턴트 답변 추가
        current_messages.append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
        st.session_state.messages[category] = current_messages
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[ERROR] 질문 처리 중 오류 발생:")
        print(error_traceback)
        error_msg = f"오류가 발생했습니다: {str(e)}\n\n상세 정보:\n{error_traceback}"
        current_messages.append({
            "role": "assistant",
            "content": error_msg,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })
        st.session_state.messages[category] = current_messages
    
    # 입력 필드 초기화를 위해 rerun
    st.rerun()

