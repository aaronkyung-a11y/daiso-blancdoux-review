"""
v2 개선사항:
1. 같은 의미 중복 키워드 병합 (예: 촉촉 + 촉촉하다 → 촉촉)
2. 스킨케어 vs 메이크업 카테고리 분류
"""
import json, os, re, math
from collections import Counter, defaultdict
from kiwipiepy import Kiwi

kiwi = Kiwi()
products = json.load(open('lab_products.json', 'r', encoding='utf-8'))
seen = set(); unique = []
for p in products:
    if p['pdNm'] in seen or p['pdNo'].startswith('B'): continue
    seen.add(p['pdNm']); unique.append(p)

STOP_NOUNS = {
    '것','거','수','때','게','줄','분','년','월','일','번','개','저','제','그','이','저희',
    '이거','저거','요거','이제','지금','다음','처음','여기','거기','저기','좀','조금','많이',
    '진짜','정말','완전','너무','굉장','약간','그냥','계속','다시','오늘','어제','내일',
    '상품','제품','사용','구매','구입','주문','배송','리뷰','후기','평가','별점','만원',
    '원','가격','할인','이벤트','행사','적립','쿠폰','포인트','쇼핑','매장','다이소',
    '브랜드','회사','이름','모델','종류','타입','성분','효과','기능','용도','방법','경우',
    '부분','점','면','곳','쪽','시간','기간','하루','매일','아침','저녁','밤','주말',
    '오래','잘','꼭','매우','아주','더','덜','가장','제일','자주','항상','늘','계','잠시',
    '선물','친구','가족','엄마','아빠','언니','동생','남편','아내','본인','저한테','그녀','남자','여자','사람',
    '느낌','생각','마음','기분','기대','고민','걱정','고생','도움',
    '중','해도','해서','한','들','들이','등','및','또','또한','그리고','하지만','근데','근',
    '바이','블랑두','다이','물광','옴므','클리어','히알','결광',
    '이건','이게','그게','저게','거기','이쪽','저쪽',
}

# 중복/동의어 병합 맵 ─ 오른쪽이 canonical form
MERGE_MAP = {
    '촉촉하다': '촉촉',          # 형용사형 → 명사형
    '건조하다': '건조',
    '쫀쫀하다': '쫀쫀',
    '산뜻하다': '산뜻',
    '상쾌하다': '상쾌',
    '끈적이다': '끈적임',
    '끈적하다': '끈적임',
    '끈적':     '끈적임',
    '밀리다':   '밀림',
    '빠르다':   '빠름',
    '순하다':   '순함',           # 순함/순해요 계열 통합
    '괜찮다':   '만족',           # "괜찮아요" → 만족으로 흡수
    '좋다':     None,             # 너무 포괄적 → 제거
    '보습력':   '보습',
    '흡수력':   '흡수',
    '발림':     '발림성',
    '유분기':   '유분',
    '물광':     None,             # 브랜드 주장 키워드 제외
    '결광':     None,
    '꿀광':     '광택',
    '자연광':   '광택',
    '자연':     None,             # 너무 모호
    '여드름':   '트러블',
    '뾰루지':   '트러블',
    '민감':     '민감성',
    '결':       '피부결',
    '크림':     None,             # 카테고리명 제외 (너무 일반)
    '토너':     None,
    '스킨':     None,
    '앰플':     None,
    '에센스':   None,
    '세럼':     None,
    '파데':     '파운데이션',
    '광':       '광택',
    '화장':     '화장(메이크업)', # 명확하게 라벨링
    '화장전':   '메이크업_전',
    '메이크업': '메이크업_전',    # "메이크업 들뜨지 않게" 맥락
}

# 스킨케어 VS 메이크업 카테고리
SKINCARE_KW = {
    '촉촉','수분','흡수','속건조','보습','쫀쫀','순함','저자극','자극','진정',
    '피부결','모공','피지','트러블','탄력','윤기','유분','각질','홍조','민감성',
    '건조','산뜻','상쾌','끈적임','피부','성분','수분감',
    '속보습','겉건조'
}
MAKEUP_KW = {
    '화장(메이크업)','메이크업_전','파운데이션','쿠션','프라이머',
    '커버','커버력','밀림','들뜸','발림성','밀착','밀착력','지속력',
    '백탁','톤업','톤다운','피부톤','틴티드','광택','민낯','쌩얼','메이크업',
    '화장','화장전','들뜨'
}

COMPOUND_PATTERNS = [
    r'속건조', r'겉건조', r'속보습', r'보습력', r'발림성', r'흡수력', r'흡수',
    r'수분감', r'수분', r'유분기', r'유분', r'윤기',
    r'쫀쫀', r'산뜻', r'상쾌', r'촉촉', r'끈적임', r'밀림',
    r'각질', r'트러블', r'여드름', r'뾰루지', r'홍조', r'피부결',
    r'피지', r'모공', r'블랙헤드',
    r'무향', r'향기', r'저자극', r'자극',
    r'주름', r'탄력', r'미백',
    r'재구매', r'만족', r'꿀템', r'가성비', r'혜자',
    r'강추', r'비추', r'후회', r'대박', r'최고',
    r'선크림', r'자외선', r'백탁',
    r'밀착력', r'지속력', r'커버력', r'톤업', r'톤다운', r'피부톤',
    r'파운데이션', r'파데', r'쿠션', r'프라이머',
    r'메이크업', r'화장전', r'민낯', r'쌩얼',
    r'민감성', r'복합성',
    r'마스크팩', r'폼클렌징', r'토너패드',
    r'꿀광', r'물광', r'결광', r'자연광',
]
COMP_RE = re.compile('|'.join(sorted(set(COMPOUND_PATTERNS), key=len, reverse=True)))

def normalize(term):
    """중복/동의어 병합. None 반환시 제외."""
    if term in MERGE_MAP:
        return MERGE_MAP[term]
    return term

def extract_terms(text):
    terms = Counter()
    if not text: return terms
    text = str(text).strip()
    for m in COMP_RE.findall(text):
        t = normalize(m)
        if t: terms[t] += 1
    try:
        toks = kiwi.tokenize(text)
    except Exception:
        return terms
    prev = None
    for t in toks:
        form, tag = t.form, t.tag
        if tag in ('NNG','NNP'):
            if len(form) >= 2 and form not in STOP_NOUNS:
                n = normalize(form)
                if n: terms[n] += 1
            if prev and prev[1] in ('NNG','NNP') and len(prev[0]) >= 1 and len(form) >= 1:
                combo = prev[0] + form
                if len(combo) >= 3 and combo not in STOP_NOUNS:
                    n = normalize(combo)
                    if n: terms[n] += 1
        elif tag == 'VA':
            if len(form) >= 2 and form not in STOP_NOUNS:
                n = normalize(form + '다')
                if n: terms[n] += 1
        prev = (form, tag)
    return terms

# Same patterns as before
DISCOVERY_PATTERNS = {
    '유튜브': r'유[튜투][버브]', '블로그': r'블로[그거]', '인스타': r'인[스슷]타|인스타그램',
    '지인추천': r'(친구|지인|동료|언니|동생|엄마|아빠|가족)\s*(?:이|가|의|한테|께|에게)?\s*(?:추천|소개|권[유해유])',
    '올리브영비교': r'올리브영|올영',
    '다이소검색': r'다이소[\s에]*[가갔간]|다이소[에서]*(?:샀|샀어|구매|구입)',
    '유명해서': r'유명[한해]|입소문|핫템|대세|인기', 
    '가성비검색': r'가성비|가격[대]?\s*(?:싸|저렴|괜찮|좋)|혜자|가격\s*착',
    '성분검색': r'(순한?|자극\s*없|저자극|민감성)\s*(?:성분|제품)|성분[이은]?\s*(?:좋|순)',
    '처음사용': r'처음\s*(?:써|사용|구[매입])|처음으?로\s*(?:써|사용)',
    '재구매': r'재구[매입]|또\s*(?:샀|구[매입])|여러\s*번\s*(?:샀|구[매입])|벌써\s*\d+[번개]',
    '선물': r'선물(?:로|하|받)',
    '브랜드팬': r'원래[ ]?(?:쓰|쓰는)|기존에[ ]?쓰[는던]|예전부터',
    '다른제품비교': r'예전[에][ ]?(?:쓰|쓰던)|다른\s*(?:브랜드|제품)|비싼\s*(?:제품|화장품)',
}

NEG_PATTERNS = {
    '자극': r'자극\s*(?:있|심|느|받|나|생[겼겨])',
    '건조': r'건조(?:해|한|함|하다|해요|했어)',
    '끈적임': r'끈적(?:거|이|함|해|하다)',
    '밀림': r'밀[려림리]',
    '향별로': r'향[이은]?\s*(?:안|별로|이상|싫|구[리려])',
    '용기불편': r'(?:뚜껑|펌프|용기|튜브)\s*(?:불편|별로|안|어[려렵]|잘\s*안)',
    '가루': r'가루[가는]\s*(?:날|생)|가루날림|백탁',
    '안맞음': r'안\s*맞(?:아|지|았|네)|맞지\s*않|맞지않|안\s*맞', 
    '트러블남': r'트러블(?:이|났|생[겼겨])|뾰루지(?:가|났)|여드름(?:이|났)',
    '기대이하': r'기대\s*(?:이하|보다\s*못)|별로|실망|그닥',
    '흡수느림': r'흡수[가]?\s*(?:안\s*|잘\s*안|느|더디|늦)',
}

def classify(term):
    """스킨케어 / 메이크업 / 기타 로 분류"""
    if term in SKINCARE_KW: return 'skincare'
    if term in MAKEUP_KW: return 'makeup'
    # Additional rules
    if re.search(r'(크림|토너|앰플|에센스|세럼|팩|마스크)', term):
        return 'skincare'
    if re.search(r'(파데|파운|쿠션|프라이머|베이스|컨실|커버|틴티드)', term):
        return 'makeup'
    return 'other'

all_corpus = defaultdict(Counter)
pos_corpus = defaultdict(Counter)
neg_corpus = defaultdict(Counter)
discovery_counts = defaultdict(Counter)
neg_counts = defaultdict(Counter)
raw_samples = defaultdict(list)

for p in unique:
    pdNo = p['pdNo']
    path = f'raw/revs_{pdNo}.json'
    if not os.path.exists(path): continue
    data = json.load(open(path, 'r', encoding='utf-8'))
    for r in data['reviews']:
        text = r.get('revwCn') or ''
        score = r.get('stscVal', 5)
        tc = extract_terms(text)
        all_corpus[pdNo] += tc
        if score >= 5:
            pos_corpus[pdNo] += tc
        elif score <= 3:
            neg_corpus[pdNo] += tc
            raw_samples[pdNo].append({"score": score, "text": text[:300]})
        for k, pat in DISCOVERY_PATTERNS.items():
            if re.search(pat, text): discovery_counts[pdNo][k] += 1
        for k, pat in NEG_PATTERNS.items():
            if re.search(pat, text): neg_counts[pdNo][k] += 1

N = len(all_corpus)
df = Counter()
for pdNo, c in all_corpus.items():
    for term in c: df[term] += 1

def tfidf(term, c, total_tokens):
    tf = c[term] / total_tokens if total_tokens else 0
    idf = math.log((N + 1) / (df[term] + 1)) + 1
    return tf * idf

result = {}
for pdNo in all_corpus:
    p = next(x for x in unique if x['pdNo']==pdNo)
    c = all_corpus[pdNo]
    total = sum(c.values())
    pc = pos_corpus[pdNo]
    nc = neg_corpus[pdNo]
    pos_total = sum(pc.values()) or 1
    neg_total = sum(nc.values()) or 1

    # Positive-distinctive keywords
    pos_kw = []
    for t, n in pc.most_common(500):
        if t in STOP_NOUNS or len(t) < 2: continue
        pos_rate = n / pos_total
        neg_rate = nc.get(t, 0) / neg_total
        if pos_rate > neg_rate * 1.2 and n >= 10:
            pos_kw.append({"term": t, "count": n,
                          "pos_rate_per_1k": round(pos_rate*1000,1),
                          "neg_rate_per_1k": round(neg_rate*1000,1),
                          "category": classify(t)})

    # Frequency top
    freq_kw = [{"term": t, "count": n, "category": classify(t)}
               for t, n in c.most_common(50)
               if t not in STOP_NOUNS and len(t) >= 2][:30]

    # Category-split: count keyword mentions per category from TOTAL corpus
    skincare_terms = [(t, n) for t, n in c.most_common(200)
                      if classify(t) == 'skincare' and t not in STOP_NOUNS and len(t) >= 2][:15]
    makeup_terms = [(t, n) for t, n in c.most_common(200)
                    if classify(t) == 'makeup' and t not in STOP_NOUNS and len(t) >= 2][:15]
    
    # Category-totals (sum of all mentions in that category)
    skincare_total = sum(n for t, n in c.items() if classify(t) == 'skincare')
    makeup_total = sum(n for t, n in c.items() if classify(t) == 'makeup')

    neg_top = [{"term": t, "count": n, "category": classify(t)}
               for t, n in nc.most_common(100)
               if t not in STOP_NOUNS and len(t) >= 2][:20]

    result[pdNo] = {
        "pdNm": p['pdNm'],
        "revwCnt": p.get('revwCnt'),
        "avgRating": p.get('avgStscVal'),
        "total_tokens": total,
        "skincare_total": skincare_total,
        "makeup_total": makeup_total,
        "skincare_keywords": [{"term": t, "count": n} for t, n in skincare_terms],
        "makeup_keywords":   [{"term": t, "count": n} for t, n in makeup_terms],
        "top_frequent": freq_kw,
        "positive_keywords": pos_kw[:20],
        "negative_keywords": neg_top,
        "discovery_mentions": [{"label": k, "count": n} for k, n in discovery_counts[pdNo].most_common()],
        "complaint_patterns": [{"label": k, "count": n} for k, n in neg_counts[pdNo].most_common()],
        "low_rating_sample": raw_samples[pdNo][:5],
    }

# Brand-level aggregation
brand_pos, brand_comp, brand_disc = Counter(), Counter(), Counter()
brand_skincare, brand_makeup = Counter(), Counter()
brand_skincare_total = brand_makeup_total = 0
for pdNo, p in result.items():
    for k in p['positive_keywords']: brand_pos[k['term']] += k['count']
    for k in p['complaint_patterns']: brand_comp[k['label']] += k['count']
    for k in p['discovery_mentions']: brand_disc[k['label']] += k['count']
    for k in p['skincare_keywords']: brand_skincare[k['term']] += k['count']
    for k in p['makeup_keywords']: brand_makeup[k['term']] += k['count']
    brand_skincare_total += p['skincare_total']
    brand_makeup_total += p['makeup_total']

products_sorted = sorted(result.values(), key=lambda x: -int(x['revwCnt']))
for p in products_sorted:
    p['pdNo'] = next(k for k,v in result.items() if v['pdNm']==p['pdNm'])

brand_summary = {
    "total_products": len(result),
    "total_reviews": sum(int(p['revwCnt']) for p in result.values()),
    "skincare_total": brand_skincare_total,
    "makeup_total": brand_makeup_total,
    "skincare_share": round(brand_skincare_total / (brand_skincare_total + brand_makeup_total) * 100, 1),
    "makeup_share":   round(brand_makeup_total / (brand_skincare_total + brand_makeup_total) * 100, 1),
    "top_skincare_brand": brand_skincare.most_common(20),
    "top_makeup_brand":   brand_makeup.most_common(20),
    "top_positive_brand": brand_pos.most_common(20),
    "top_complaints_brand": brand_comp.most_common(15),
    "top_discovery_brand": brand_disc.most_common(15),
}

with open('keywords_by_product_v2.json','w',encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
with open('brand_summary_v2.json','w',encoding='utf-8') as f:
    json.dump(brand_summary, f, ensure_ascii=False, indent=2)
with open('report_data_v2.json','w',encoding='utf-8') as f:
    json.dump(products_sorted, f, ensure_ascii=False, indent=2)

print(f"Processed {N} products. Total tokens: {sum(sum(c.values()) for c in all_corpus.values())}")
print(f"\n[Brand scope: 스킨케어 vs 메이크업 언어]")
print(f"  스킨케어 언급:  {brand_skincare_total:,}  ({brand_summary['skincare_share']}%)")
print(f"  메이크업 언급: {brand_makeup_total:,}  ({brand_summary['makeup_share']}%)")

print("\n[TOP 스킨케어 키워드 (브랜드 전체)]")
for t,n in brand_skincare.most_common(10): print(f"  {t:>10}  {n:,}")
print("\n[TOP 메이크업 키워드 (브랜드 전체)]")
for t,n in brand_makeup.most_common(10): print(f"  {t:>10}  {n:,}")
