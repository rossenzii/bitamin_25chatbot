import os, json
from langchain_core.documents import Document

# === 1. 커리큘럼 ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
CURRICULUM_DB_PATH = os.path.join(BASE_DIR, "member_db", "curriculum.json")

with open(CURRICULUM_DB_PATH, encoding="utf-8") as f:
    data = json.load(f)
curri_docs = []

# 학기
for part_data in data.get("학기 세션 일정", []):
    회차 = part_data["회차"]   # 예: "1회차"
    for session in part_data["세션"]:
        text = f"[{회차}] {session['주제']} - {', '.join(session['내용'])}"
        curri_docs.append(Document(page_content=text, metadata={"type": "session", "part": 회차}))

# 방학 
for part_data in data.get("방학 세션 일정", []):
    주차 = part_data["주차"]   # 예: "1주차"
    for session in part_data["세션"]:
        text = f"[방학 {주차}] {session['주제']} - {', '.join(session['내용'])}"
        curri_docs.append(Document(page_content=text, metadata={"type": "session", "part": f"방학 {주차}"}))

__all__ = ["curri_docs"]


# === 2. 멤버 DB ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
MEMBER_DB_PATH = os.path.join(BASE_DIR, "member_db", "info1516.json")

with open(MEMBER_DB_PATH, "r", encoding="utf-8") as f:
    members = json.load(f)
memb_docs = []

# === 통계 정보 Document 추가 ===
total_count = len(members)

# 15기: 앞 29명, 16기: 나머지 30명
기수15_members = members[:29]
기수16_members = members[29:]

# 전체 통계
male_count = sum(1 for m in members if m['성별'] == '남')
female_count = sum(1 for m in members if m['성별'] == '여')
운영진_count = sum(1 for m in members if m['운영진/부서'] not in ['멤버', ''])

# 15기 통계
기수15_male = sum(1 for m in 기수15_members if m['성별'] == '남')
기수15_female = sum(1 for m in 기수15_members if m['성별'] == '여')
기수15_운영진 = sum(1 for m in 기수15_members if m['운영진/부서'] not in ['멤버', ''])

# 16기 통계
기수16_male = sum(1 for m in 기수16_members if m['성별'] == '남')
기수16_female = sum(1 for m in 기수16_members if m['성별'] == '여')
기수16_운영진 = sum(1 for m in 기수16_members if m['운영진/부서'] not in ['멤버', ''])

# 전체 통계 정보
stats_text = f"""비타민 동아리 멤버 통계 정보:
- 총 인원: {total_count}명 (15기 + 16기 통합)
  * 15기: {len(기수15_members)}명 (남 {기수15_male}명, 여 {기수15_female}명, 운영진 {기수15_운영진}명)
  * 16기: {len(기수16_members)}명 (남 {기수16_male}명, 여 {기수16_female}명, 운영진 {기수16_운영진}명)
- 전체 남성: {male_count}명
- 전체 여성: {female_count}명
- 전체 운영진: {운영진_count}명
- 일반 멤버: {total_count - 운영진_count}명
"""
memb_docs.append(Document(page_content=stats_text, metadata={"type": "member_stats", "summary": True}))

# === 부서별 인원 통계 ===
부서_통계 = {}
for m in members:
    부서 = m['운영진/부서']
    if 부서 not in 부서_통계:
        부서_통계[부서] = {"total": 0, "male": 0, "female": 0}
    부서_통계[부서]["total"] += 1
    if m['성별'] == '남':
        부서_통계[부서]["male"] += 1
    else:
        부서_통계[부서]["female"] += 1

부서_text = "비타민 동아리 부서별 인원 통계:\n"
for 부서, 통계 in 부서_통계.items():
    부서_text += f"- {부서}: 총 {통계['total']}명 (남 {통계['male']}명, 여 {통계['female']}명)\n"

memb_docs.append(Document(page_content=부서_text, metadata={"type": "department_stats", "summary": True}))

# === MBTI 통계 ===
mbti_통계 = {}
for m in members:
    mbti = m['MBTI']
    mbti_통계[mbti] = mbti_통계.get(mbti, 0) + 1

mbti_text = "비타민 동아리 MBTI 분포:\n"
for mbti, count in sorted(mbti_통계.items(), key=lambda x: x[1], reverse=True):
    mbti_text += f"- {mbti}: {count}명\n"

memb_docs.append(Document(page_content=mbti_text, metadata={"type": "mbti_stats", "summary": True}))

# === 학교 통계 (개인 식별 불가능하도록 집계만) ===
학교_통계 = {}
for m in members:
    학교 = m['학교']
    학교_통계[학교] = 학교_통계.get(학교, 0) + 1

학교_text = "비타민 동아리 학교별 인원 분포:\n"
for 학교, count in sorted(학교_통계.items(), key=lambda x: x[1], reverse=True):
    학교_text += f"- {학교}: {count}명\n"

memb_docs.append(Document(page_content=학교_text, metadata={"type": "school_stats", "summary": True}))

# === 주의: 개별 멤버의 개인정보(학교+성별+나이)는 저장하지 않음 ===
# 개인정보 보호를 위해 통계 정보만 제공


__all__ = ["memb_docs"]