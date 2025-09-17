import requests
from bs4 import BeautifulSoup
import time
import json

headers = {
    "User-Agent": "Mozilla/5.0"
}
base_url = "https://dacon.io"
main_url = f"{base_url}/competitions"

# 1. 대회 목록 페이지에서 제목 + 상세 URL 수집
def get_competition_list():
    response = requests.get(main_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    competitions = []
    title_tags = soup.find_all("p", class_="name ellipsis")

    for tag in title_tags:
        title = tag.text.strip()
        parent_a = tag.find_parent("a")
        if parent_a and parent_a["href"]:
            full_url = base_url + parent_a["href"]
            competitions.append({
                "title": title,
                "url": full_url
            })

    return competitions

# 2. 전체 크롤링 흐름
def crawl_dacon_competitions():
    all_data = []
    comp_list = get_competition_list()

    for comp in comp_list:
        print(f"크롤링 중: {comp['title']}")
        all_data.append(comp)
    return all_data

# 실행
data = crawl_dacon_competitions()

# JSON 파일로 저장
with open("dacon.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("크롤링 완료")


