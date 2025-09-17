import fitz  
import os

pdf_path = "./project_db/1415S/시계열1조_신뢰할 수 있는 의료데이터 AI 모델, 수면 데이터를 중심으로.pdf"
doc = fitz.open(pdf_path)

# 슬라이드별 텍스트 추출
slide_texts = []

for page_num, page in enumerate(doc):
    text = page.get_text("text")
    cleaned_text = text.strip()
    slide_texts.append({
        "page": page_num + 1,
        "text": cleaned_text
    })

# 출력
for slide in slide_texts:
    print(f"Slide {slide['page']} ------------------")
    print(slide["text"])

# 파일로 저장
with open("slides_text_output2.txt", "w", encoding="utf-8") as f:
    for slide in slide_texts:
        f.write(f"## Slide {slide['page']}\n")
        f.write(slide["text"] + "\n\n")