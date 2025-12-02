# Streamlit Cloud 배포 가이드

## 🚀 배포 전 체크리스트

### 1. **requirements.txt 확인**
```bash
langchain>=0.1.0
langchain-community>=0.0.38
langchain-openai>=0.0.5
langchain-experimental>=0.0.50
langchain-huggingface>=0.0.1
langchain-core>=0.1.0
openai>=1.6.1
faiss-cpu>=1.7.4
transformers>=4.35.0
torch>=2.0.0
sentencepiece>=0.1.99
python-dotenv>=1.0.0
numpy>=1.24.0
tqdm>=4.65.0
streamlit>=1.28.0
jq>=1.6.0
rank-bm25>=0.2.2
```

### 2. **FAISS 인덱스 파일 포함**
`.gitignore`에서 인덱스 파일이 제외되어 있으므로, **반드시 Git에 포함**시켜야 합니다.

```bash
# .gitignore에서 다음 줄들을 주석 처리하거나 삭제
# **/rag_faiss_index/
# *.faiss
# *.pkl
```

**또는** 특정 인덱스만 포함:

```bash
# 인덱스 파일 강제 추가
git add -f project/project_rag/rag_faiss_index/
git add -f contest_jw/rag_faiss_index/
git add -f member/hybrid_rag/rag_faiss_index/
```

### 3. **Streamlit Cloud 설정**

#### Step 1: GitHub에 푸시
```bash
git add .
git commit -m "배포 준비: config 오류 수정, 환경 변수 설정"
git push origin streamlit
```

#### Step 2: Streamlit Cloud 대시보드 접속
1. https://share.streamlit.io/ 접속
2. "New app" 클릭
3. Repository 선택: `your-repo-name`
4. Branch 선택: `streamlit`
5. Main file path: `streamlit_app.py`

#### Step 3: Secrets 설정
Streamlit Cloud 대시보드에서:
1. 배포된 앱 선택
2. **Settings** > **Secrets** 클릭
3. 다음 내용 입력:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your-openai-api-key-here"
HUGGINGFACEHUB_API_TOKEN = "your-huggingface-token-here"
```

4. **Save** 클릭

#### Step 4: 앱 재시작
- Settings > Reboot app

---

## 🔍 로컬에서 배포 테스트

배포 전에 로컬에서 테스트하려면:

```bash
# 1. 환경 변수 확인
echo $OPENAI_API_KEY

# 2. Streamlit Secrets 파일 생성 (로컬 테스트용)
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
OPENAI_API_KEY = "your-api-key-here"
HUGGINGFACEHUB_API_TOKEN = "your-token-here"
EOF

# 3. 실행
streamlit run streamlit_app.py
```

---

## ⚠️ 주의사항

### 1. **대용량 파일 제한**
- GitHub 파일 크기 제한: 100MB
- FAISS 인덱스 크기 확인:
  ```bash
  ls -lh project/project_rag/rag_faiss_index/
  ls -lh contest_jw/rag_faiss_index/
  ls -lh member/hybrid_rag/rag_faiss_index/
  ```

- **contest_jw/rag_faiss_index/index.faiss (26MB)** ← 가장 큼
- project: 3.9MB
- member: 558KB

**✅ 모두 100MB 이하이므로 문제없음!**

### 2. **데이터 파일**
현재 `.gitignore`에 다음이 제외되어 있음:
- `member_db/*.xlsx`
- `project_txt/`
- `tami/data_sources/`

**인덱스만 있으면 실행 가능하므로 원본 데이터는 제외해도 됨**

### 3. **환경 변수 누락 시**
만약 Secrets 설정을 잊어버렸다면, 앱 로그에 다음과 같은 오류가 표시됩니다:
```
OPENAI_API_KEY is not set
```

해결:
1. Settings > Secrets에서 API 키 추가
2. Reboot app

---

## 🐛 배포 후 디버깅

### 로그 확인
Streamlit Cloud 대시보드 > **Manage app** > **Logs**

### 일반적인 오류와 해결책

| 오류 | 원인 | 해결 |
|------|------|------|
| `No module named 'config'` | import 경로 문제 | ✅ 이미 수정됨 (환경 변수 우선 사용) |
| `OPENAI_API_KEY not found` | Secrets 미설정 | Settings > Secrets 추가 |
| `FAISS index not found` | 인덱스 파일 미포함 | Git에 인덱스 파일 추가 |
| `Memory limit exceeded` | 메모리 부족 | Streamlit Cloud는 1GB 제한. 인덱스 최적화 필요 |

---

## 📊 현재 상태

### ✅ 완료된 작업
1. ✅ `requirements.txt` 업데이트
2. ✅ 환경 변수 로딩 개선 (Streamlit Secrets 지원)
3. ✅ 모든 `config.settings` import를 환경 변수 우선으로 변경
4. ✅ OpenMP 충돌 방지 (`KMP_DUPLICATE_LIB_OK=TRUE`)
5. ✅ 디버그 로깅 추가
6. ✅ `.gitignore`에 `secrets.toml` 추가

### 📝 배포 시 필요한 작업
1. **FAISS 인덱스 Git에 포함** (현재 제외됨)
2. **Streamlit Cloud Secrets 설정**
3. **GitHub 푸시**

---

## 🚀 빠른 배포 명령어

```bash
# 1. 인덱스 파일 포함
git add -f project/project_rag/rag_faiss_index/
git add -f contest_jw/rag_faiss_index/
git add -f member/hybrid_rag/rag_faiss_index/

# 2. 커밋 & 푸시
git add .
git commit -m "배포 준비: 인덱스 포함, config 오류 수정"
git push origin streamlit

# 3. Streamlit Cloud에서:
#    - New app 생성
#    - Secrets 설정
#    - Deploy!
```

완료! 🎉

