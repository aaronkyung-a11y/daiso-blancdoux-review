# 더랩 바이 블랑두 · 다이소몰 VOC 분석 (v2)

**The Lab by Blanc Doux × Daiso Mall — Voice-of-Customer Keyword Analysis**

다이소몰에 등록된 더랩 바이 블랑두 전 제품(15종)의 리뷰 **10,462건**과 구조화 설문 데이터를 전수 수집 · 형태소 분석 · 키워드 분류하여, 브랜드가 주장하는 키워드가 아닌 **고객이 실제로 쓰는 언어**로 재구성한 포지셔닝 리포트.

<p align="center">
  <img alt="dashboard screenshot placeholder" src="https://img.shields.io/badge/products-15-2C2C2C?style=for-the-badge" />
  <img alt="reviews" src="https://img.shields.io/badge/reviews-10,462-7D5835?style=for-the-badge" />
  <img alt="skincare vs makeup" src="https://img.shields.io/badge/skincare%20vs%20makeup-78.9%25%20%3A%2021.1%25-4A6B7D?style=for-the-badge" />
</p>

## 핵심 발견

1. **고객의 21%는 이 브랜드를 메이크업 제품으로 말한다.** 총 키워드 언급 중 메이크업 관련 3,544건(21.1%). 틴티드 커버 크림은 메이크업 언급이 51.2%로 카테고리 분류 자체 재검토감.
2. **브랜드 삼위일체 = 촉촉 · 순함 · 가성비.** 다만 다이소 기초제품 전반에 흔한 틀이라 진짜 차별화는 use-case(결광·옴므) 라인 세분화에서 나옴.
3. **기대-성능 갭 = "건조" 353건.** 주장 키워드가 "물광·히알·수분"인데 ★1~3 리뷰 최다 불만이 "건조". 속건조 대응 파생 SKU 기회.
4. **올리브영 비교 유입 ≈ 유튜브 유입.** 다이소는 "저가 채널"이 아니라 "올영에서 갈아타는 채널"로 재정의 중.
5. **저노출 히어로 후보 2종.** 결광 선에센스(★4.7, 168건), 옴므 선크림(★4.9, 153건)이 리뷰 수 대비 만족·긍정 집중도 최상위.

## 결과물 보기

- **`outputs/dashboard.html`** — 인터랙티브 에디토리얼 대시보드. 브라우저로 바로 열면 전체 분석을 탐색 가능.
- **`outputs/analysis.xlsx`** — 17개 시트 엑셀 리포트(개요, 카테고리분할, 제품별 15종). 238개 수식 포함.

## 저장소 구조

```
blancdoux-voc/
├── README.md                        # 이 문서
├── .gitignore
├── outputs/                         # 최종 산출물
│   ├── dashboard.html               # 인터랙티브 HTML 대시보드
│   └── analysis.xlsx                # 공유용 Excel 리포트
├── data/                            # 가공된 분석 데이터
│   ├── products.json                # 제품 리스트 + 메타데이터
│   ├── attrs_by_product.json        # 다이소 구조화 설문(피부타입/보습력/자극/향)
│   ├── keywords_by_product_v2.json  # 제품별 전체 키워드 분석(v2)
│   ├── brand_summary_v2.json        # 브랜드 전체 집계(v2)
│   └── report_data_v2.json          # HTML/Excel 입력용 통합 데이터(v2)
├── raw/                             # 원본 크롤 데이터 (15 × 2 = 30 JSON)
│   ├── revs_{pdNo}.json             # 제품별 전체 리뷰 본문
│   └── attr_{pdNo}.json             # 제품별 구조화 설문 원본
└── src/                             # 재현용 스크립트
    ├── crawler.py                   # 다이소몰 크롤러
    ├── analyze.py                   # 키워드 추출·병합·카테고리 분류
    ├── build_dashboard.py           # HTML 대시보드 생성
    └── build_spreadsheet.py         # Excel 리포트 생성
```

## 재현 방법

### 1. 환경

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests kiwipiepy openpyxl
```

### 2. 실행 순서

```bash
# (원본 데이터가 raw/에 이미 있어서 크롤링은 생략 가능. 최신화 원하면 실행.)
python src/crawler.py

# 키워드 분석 (병합 + 카테고리 분류)
python src/analyze.py

# 산출물 생성
python src/build_dashboard.py       # → outputs/dashboard.html
python src/build_spreadsheet.py     # → outputs/analysis.xlsx
```

### 3. 엑셀 수식 재계산(선택)

Excel을 한 번 열었다 저장하면 자동. 커맨드라인에선 LibreOffice 필요.

## 방법론

### 데이터 수집

- **소스**: `daisomall.co.kr`의 공개 리뷰·구조화 설문 API (`/pd/pds/revw/selRevwList`, `/pd/pds/revw/selRevwAttr`)
- **제품 발견**: 브랜드명 검색 API(`/ssn/search/SearchGoods`)에서 16개 SKU 획득, 중복 번들 1건 제거 → 15개
- **리뷰**: 제품별 페이지네이션(pageSize=500)으로 전수 수집. 정렬 `RGDT`(등록일순)로 랭킹 바이어스 최소화. 500ms throttle.
- **수집일**: 2026-04-22

### 키워드 추출 파이프라인

1. **형태소 분석**: Kiwi(한국어) `NNG/NNP`(명사), `VA`(형용사) 추출, 2글자 이상, 사용자 정의 불용어 리스트로 1차 필터.
2. **복합 패턴**: 한국어 뷰티 업계 특화 정규식 패턴 약 60종(속건조·발림성·백탁·톤업 등).
3. **N-gram**: 연속 명사 2-gram 결합(피부+결 → 피부결).
4. **동의어 병합**(v2 신규)
   - `촉촉/촉촉하다` → `촉촉`, `건조/건조하다` → `건조`, `흡수/흡수력` → `흡수` 등 15쌍.
   - 브랜드 주장어(`물광`, `결광`), 카테고리명(`크림`, `토너`, `앰플` 등), 모호 일반어(`좋다`, `자연`) 제거.
5. **카테고리 분류**(v2 신규): 스킨케어 / 메이크업 / 기타 3분할.
   - 스킨케어: 촉촉·수분·흡수·속건조·보습·쫀쫀·순함·자극·진정·피부결·모공·트러블·유분 등
   - 메이크업: 화장·메이크업·파운데이션·쿠션·커버·발림성·밀착·밀림·들뜸·톤업·백탁·틴티드·광택 등
6. **감정 분할**: ★5 vs ★1~3 리뷰 분리 후 카이제곱 유사 지표(긍정빈도/부정빈도)로 **긍정 집중 키워드** 산출.
7. **TF-IDF**: 15개 제품을 문서로 간주, 제품별 **고유 키워드**(diagnostic term) 산출.
8. **유입/불만 패턴 태깅**: 약 25개 정규식 패턴으로 Discovery 채널 + Complaint 패턴 분류.

### 알려진 한계

- 리뷰 특성상 양극단(만족/불만) 과잉, 중간 체험 과소.
- 카테고리 분류는 수기 사전 기반이라 맥락상 모호한 단어(`피부`, `얼굴`)는 '기타'로 분류. 확장 가능.
- 구매 전 의도를 직접 측정할 채널은 없음 — Q&A 엔드포인트 미존재. 대신 리뷰 내 "왜 샀나" 맥락(재구매·가성비검색·유튜브 등)을 정규식으로 근사.
- API 응답은 비공식 엔드포인트 역공학 결과로, 스키마 변경시 크롤러 수정 필요.

## 엔지니어링 노트

### API 엔드포인트

| 용도 | 엔드포인트 | 메서드 |
|---|---|---|
| 브랜드 제품 검색 | `https://www.daisomall.co.kr/ssn/search/SearchGoods?searchTerm=...` | GET |
| 리뷰 리스트 | `https://fapi.daisomall.co.kr/pd/pds/revw/selRevwList` | POST |
| 리뷰 속성(설문) | `https://fapi.daisomall.co.kr/pd/pds/revw/selRevwAttr` | POST |

요청 시 `Referer: https://www.daisomall.co.kr/` 및 `Origin: https://www.daisomall.co.kr` 헤더 필수.

### 리뷰 API 요청 예시

```json
POST /pd/pds/revw/selRevwList
{
  "pdNo": "1060645",
  "pageSize": 500,
  "currentPage": 1,
  "filter": "ALL",
  "sortCond": "RGDT",
  "useCommonPaging": false,
  "cttsOnlyYn": "N",
  "onldPdNoList": []
}
```

응답 `data.pdRevwList[].revwCn`에 본문, `stscVal`에 별점(1~5), `totalCnt`에 총 리뷰 수.

## 윤리 · 이용 정책

- 공개된 리뷰 데이터만을 분석 목적으로 수집했으며, 요청당 500ms 지연으로 서버 부하를 최소화했습니다.
- 개별 작성자 식별 정보는 저장하지 않습니다(리뷰 본문 내 익명 닉네임은 원본 데이터에 포함되나 분석 산출물에서는 사용하지 않음).
- 본 저장소는 **내부 제품기획 목적**의 사용을 전제로 작성되었으며, 외부 공개 · 상업적 재배포 시 다이소몰 이용약관 확인 후 진행 바랍니다.

## 라이선스

내부 사용 — Internal use only. 별도 라이선스 지정 전까지 외부 공개 금지.

---

*Compiled 2026-04-22 · Built with Kiwi, openpyxl, and custom Korean beauty VOC lexicon.*
