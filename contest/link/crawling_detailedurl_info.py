import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers = {
    "User-Agent": "Mozilla/5.0"
}

def append_detail_urls(data: list) -> list:
    updated = []

    for item in data:
        base_url = item.get("url")
        if not base_url:
            continue

        detail_urls = set()
        # 1. 바로 접근 가능한 description 페이지 있는지 확인
        direct_url = base_url.rstrip("/") + "/description"
        res = requests.get(direct_url, headers=headers)

        if res.status_code == 200 and "준비 중" not in res.text:
            detail_urls.add(direct_url)

        # 2. overview 페이지에서 <a href="/competitions/.../overview/description"> 수집
        try:
            res = requests.get(base_url, headers=headers)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                a_tags = soup.find_all("a", href=True)

                for a in a_tags:
                    href = a["href"]
                    if "/overview/description" in href and "login" not in href:
                        full_url = urljoin("https://dacon.io", href)
                        detail_urls.add(full_url)

        except Exception as e:
            print(f"{base_url} 처리 중 오류 발생: {e}")

        # 추가한 detail URL들을 리스트로 저장
        item["detail_urls"] = list(detail_urls)
        updated.append(item)

    return updated