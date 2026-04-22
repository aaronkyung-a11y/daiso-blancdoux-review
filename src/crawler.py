import json, time, os, requests, sys
from pathlib import Path

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Referer": "https://www.daisomall.co.kr/",
    "Origin": "https://www.daisomall.co.kr",
    "Accept": "application/json, text/plain, */*",
}
BASE = "https://fapi.daisomall.co.kr"

def post(path, body):
    r = requests.post(BASE + path, headers=HEADERS, json=body, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_attr(pdNo):
    return post("/pd/pds/revw/selRevwAttr", {"pdNo": pdNo})

def fetch_reviews(pdNo, page_size=500):
    all_revs = []
    page = 1
    total = None
    while True:
        body = {
            "pdNo": pdNo, "pageSize": page_size, "currentPage": page,
            "filter": "ALL", "sortCond": "RGDT",  # use RGDT to get newest first and avoid ranking bias
            "useCommonPaging": False, "cttsOnlyYn": "N", "onldPdNoList": []
        }
        d = post("/pd/pds/revw/selRevwList", body)
        revs = d['data'].get('pdRevwList', [])
        if not revs:
            break
        if total is None and revs:
            total = revs[0].get('totalCnt', 0)
        all_revs.extend(revs)
        print(f"  pdNo={pdNo} page {page}: got {len(revs)} (total so far: {len(all_revs)}/{total})", flush=True)
        if len(revs) < page_size or (total and len(all_revs) >= total):
            break
        page += 1
        time.sleep(0.5)  # respectful delay
    return all_revs, total

products = json.load(open('lab_products.json', 'r', encoding='utf-8'))
# Dedupe (there was a duplicate with pdNo B202...)
seen = set()
unique = []
for p in products:
    key = p['pdNm']
    if key in seen: continue
    seen.add(key)
    unique.append(p)
# Keep only standard pdNos (drop bundle B...)
unique = [p for p in unique if not p['pdNo'].startswith('B')]
print(f"Unique products to crawl: {len(unique)}", flush=True)

os.makedirs('raw', exist_ok=True)

summary = []
for i, p in enumerate(unique):
    pdNo = p['pdNo']
    print(f"\n[{i+1}/{len(unique)}] {p['pdNm']} (pdNo={pdNo}, expected {p['revwCnt']} revs)", flush=True)
    try:
        attr = fetch_attr(pdNo)
        with open(f'raw/attr_{pdNo}.json', 'w', encoding='utf-8') as f:
            json.dump(attr, f, ensure_ascii=False)
    except Exception as e:
        print(f"  attr error: {e}", flush=True)
        attr = None
    try:
        revs, total = fetch_reviews(pdNo, page_size=500)
        with open(f'raw/revs_{pdNo}.json', 'w', encoding='utf-8') as f:
            json.dump({"pdNo": pdNo, "pdNm": p['pdNm'], "totalCnt": total, "reviews": revs}, f, ensure_ascii=False)
        summary.append({
            "pdNo": pdNo, "pdNm": p['pdNm'], "fetched_reviews": len(revs),
            "total_reviews": total, "avgRating": p.get('avgStscVal'),
        })
    except Exception as e:
        print(f"  review error: {e}", flush=True)
    time.sleep(0.5)

with open('crawl_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print("\nCrawl complete!")
print(json.dumps(summary, ensure_ascii=False, indent=2))
