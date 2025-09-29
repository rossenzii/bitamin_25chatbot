import json
from langchain.schema import Document

# === 3. 비타민 정보 ===
with open("./member_db/docs.json", encoding="utf-8") as f:
    bitamin_data = json.load(f)
bita_docs = []
# 모집 일정
for role, schedule in bitamin_data["bitamin"]["모집 일정"].items():
    for key, value in schedule.items():
        text = f"[모집 일정 - {role}] {key}: {value}"
        bita_docs.append(Document(page_content=text, metadata={"type": "schedule", "role": role}))

# 문의
for key, value in bitamin_data["bitamin"]["문의"].items():
    text = f"[문의] {key}: {value}"
    bita_docs.append(Document(page_content=text, metadata={"type": "contact"}))

# 공모전 수상 내역
for award in bitamin_data["bitamin"]["공모전 수상 내역"]:
    bita_docs.append(Document(page_content=f"[공모전 수상 내역] {award}", metadata={"type": "award"}))

# 정기 세션 일정
for key, value in bitamin_data["bitamin"]["정기 세션 일정"].items():
    text = f"[정기 세션 일정] {key}: {value}"
    bita_docs.append(Document(page_content=text, metadata={"type": "regular_session"}))


# 연간 정기 세션 일정
for key, value in bitamin_data["bitamin"]["연간 정기 세션 일정"].items():
    text = f"[연간 정기 세션 일정] {key}: {value}"
    bita_docs.append(Document(page_content=text, metadata={"type": "annual_session"}))

# 스터디
for key, value in bitamin_data["bitamin"]["스터디"].items():
    if isinstance(value, list):
        text = f"[스터디] {key}: {', '.join(value)}"
    else:
        text = f"[스터디] {key}: {value}"
    bita_docs.append(Document(page_content=text, metadata={"type": "study"}))

# 현직자 초청 강연
for key, value in bitamin_data["bitamin"]["현직자 초청 강연"].items():
    if isinstance(value, dict):
        for sub_key, sub_value in value.items():
            text = f"[현직자 초청 강연] {key} - {sub_key}: {sub_value}"
            bita_docs.append(Document(page_content=text, metadata={"type": "lecture"}))
    else:
        text = f"[현직자 초청 강연] {key}: {value}"
        bita_docs.append(Document(page_content=text, metadata={"type": "lecture"}))

# MT&소모임
for key, value in bitamin_data["bitamin"]["MT&소모임"].items():
    if isinstance(value, dict):
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, list):
                text = f"[MT&소모임] {key} - {sub_key}: {', '.join(sub_value)}"
            else:
                text = f"[MT&소모임] {key} - {sub_key}: {sub_value}"
            bita_docs.append(Document(page_content=text, metadata={"type": "activity"}))
    else:
        text = f"[MT&소모임] {key}: {value}"
        bita_docs.append(Document(page_content=text, metadata={"type": "activity"}))

# 프로젝트 컨퍼런스
for key, value in bitamin_data["bitamin"]["프로젝트 컨퍼런스"].items():
    if isinstance(value, list):
        text = f"[프로젝트 컨퍼런스] {key}: {', '.join(value)}"
    elif isinstance(value, dict):
        for sub_key, sub_value in value.items():
            text = f"[프로젝트 컨퍼런스] {key} - {sub_key}: {sub_value}"
            bita_docs.append(Document(page_content=text, metadata={"type": "conference"}))
    else:
        text = f"[프로젝트 컨퍼런스] {key}: {value}"
        bita_docs.append(Document(page_content=text, metadata={"type": "conference"}))

# 연합 데이터톤
for key, value in bitamin_data["bitamin"]["연합 데이터톤"].items():
    if isinstance(value, list):
        text = f"[연합 데이터톤] {key}: {', '.join(value)}"
    elif isinstance(value, dict):
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, list):
                text = f"[연합 데이터톤] {key} - {sub_key}: {', '.join(sub_value)}"
            else:
                text = f"[연합 데이터톤] {key} - {sub_key}: {sub_value}"
            bita_docs.append(Document(page_content=text, metadata={"type": "datathon"}))
    else:
        text = f"[연합 데이터톤] {key}: {value}"
        bita_docs.append(Document(page_content=text, metadata={"type": "datathon"}))


# FAQ
for faq in bitamin_data["faq"]:
    text = f"Q: {faq['question']} A: {faq['answer']}"
    bita_docs.append(Document(page_content=text, metadata={"type": "faq"}))


__all__ = ["bita_docs"]
