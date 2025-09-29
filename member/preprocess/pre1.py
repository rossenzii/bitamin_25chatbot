import json
from langchain.schema import Document

# === 1. 커리큘럼 ===

with open("./member_db/curriculum.json", encoding="utf-8") as f:
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
with open("./member_db/info1516.json", "r", encoding="utf-8") as f:
    members = json.load(f)
memb_docs = []
for m in members:
    text = f"{m['학교']} {m['성별']} ({m['나이']} 출생) | MBTI: {m['MBTI']} | 부서: {m['운영진/부서']}"
    memb_docs.append(Document(page_content=text, metadata={"type": "member"}))


__all__ = ["memb_docs"]