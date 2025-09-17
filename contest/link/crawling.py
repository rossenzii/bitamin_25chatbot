import json
from crawling_detailedurl_info import append_detail_urls

with open("dacon.json", "r", encoding="utf-8") as f:
    competitions = json.load(f) 
updated_data = append_detail_urls(competitions)

with open("dacon_url_detail.json", "w", encoding="utf-8") as f:
    json.dump(updated_data, f, indent=2, ensure_ascii=False)

print("detail_url 추가 완료!")