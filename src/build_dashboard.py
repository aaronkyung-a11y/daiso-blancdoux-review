import json

products = json.load(open('report_data_v2.json','r',encoding='utf-8'))
brand = json.load(open('brand_summary_v2.json','r',encoding='utf-8'))

# Compute per-product makeup%
for p in products:
    tot = p['skincare_total'] + p['makeup_total']
    p['makeup_pct'] = round(p['makeup_total'] / tot * 100, 1) if tot else 0
    p['skincare_pct'] = round(p['skincare_total'] / tot * 100, 1) if tot else 0

data_js = json.dumps({"products": products, "brand": brand}, ensure_ascii=False)

HTML = r'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Lab by Blanc Doux · VOC Analysis</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,400&family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#f7f4ed;
  --bg-card:#fffefa;
  --ink:#1a1815;
  --ink-soft:#5a5349;
  --ink-mute:#958c7e;
  --accent:#7d5835;
  --accent-soft:#c9b697;
  --accent-bg:#ede3d2;
  --pos:#3a6b4d;
  --pos-bg:#e3efe7;
  --neg:#a8433a;
  --neg-bg:#f2dcd8;
  --skincare:#4a6b7d;
  --skincare-bg:#dfe8ef;
  --makeup:#a85a6b;
  --makeup-bg:#f2dce2;
  --line:#e5ddcf;
  --shadow:0 1px 0 rgba(29,24,18,.04), 0 8px 28px rgba(29,24,18,.06);
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg);color:var(--ink);font-family:'IBM Plex Sans KR',system-ui,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}
body{padding:24px 20px 80px;max-width:1280px;margin:0 auto}
.serif{font-family:'Cormorant Garamond',serif}
.mono{font-family:'IBM Plex Mono',monospace;letter-spacing:.02em}

.masthead{border-bottom:1px solid var(--ink);padding-bottom:24px;margin-bottom:32px;position:relative}
.masthead::before{content:"";position:absolute;inset:auto 0 -4px 0;height:1px;background:var(--ink)}
.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:500;letter-spacing:.22em;text-transform:uppercase;color:var(--accent);margin-bottom:16px;display:flex;justify-content:space-between;align-items:baseline}
.eyebrow .date{color:var(--ink-mute);letter-spacing:.12em}
h1.title{font-family:'Cormorant Garamond',serif;font-weight:400;font-size:clamp(38px,6vw,72px);line-height:.98;letter-spacing:-.01em;margin-bottom:10px;font-style:italic}
h1.title b{font-style:normal;font-weight:500}
.subtitle{font-size:14px;color:var(--ink-soft);max-width:640px;margin-top:18px}
.badgeline{display:flex;flex-wrap:wrap;gap:8px;margin-top:22px}
.badge{font-family:'IBM Plex Mono',monospace;font-size:10.5px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;padding:6px 12px;border:1px solid var(--ink);background:transparent;color:var(--ink);border-radius:2px}
.badge.accent{background:var(--ink);color:var(--bg)}
.badge.v2{background:var(--accent);color:#fff;border-color:var(--accent)}

.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:40px 0 56px}
.stat{background:var(--bg-card);padding:24px 20px}
.stat .k{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:8px}
.stat .v{font-family:'Cormorant Garamond',serif;font-size:42px;font-weight:400;line-height:1;color:var(--ink)}
.stat .v small{font-size:15px;color:var(--ink-mute);margin-left:4px;font-family:'IBM Plex Sans KR',sans-serif}

section{margin-bottom:72px}
.section-head{display:flex;align-items:baseline;gap:18px;margin-bottom:28px;padding-bottom:14px;border-bottom:1px solid var(--ink)}
.section-num{font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:500;color:var(--accent);letter-spacing:.15em}
.section-head h2{font-family:'Cormorant Garamond',serif;font-weight:500;font-size:32px;letter-spacing:-.01em;flex:1}
.section-head .meta{font-size:11px;color:var(--ink-mute);font-family:'IBM Plex Mono',monospace;letter-spacing:.08em}

/* Split bar for skincare/makeup */
.split-hero{background:var(--bg-card);border:1px solid var(--line);padding:36px 32px;box-shadow:var(--shadow);margin-bottom:32px}
.split-hero .splitline{font-family:'Cormorant Garamond',serif;font-size:26px;font-style:italic;color:var(--ink);line-height:1.3;margin-bottom:24px}
.split-hero .splitline em{font-style:normal;color:var(--accent);font-weight:500}
.split-bar{height:48px;display:flex;border:1px solid var(--ink);background:#fff;margin-bottom:14px;overflow:hidden}
.split-bar .sk{background:var(--skincare);display:flex;align-items:center;justify-content:flex-start;padding-left:18px;color:#fff;font-family:'Cormorant Garamond',serif;font-size:24px;font-weight:500;font-style:italic;transition:width .6s ease}
.split-bar .mk{background:var(--makeup);display:flex;align-items:center;justify-content:flex-end;padding-right:18px;color:#fff;font-family:'Cormorant Garamond',serif;font-size:24px;font-weight:500;font-style:italic;transition:width .6s ease}
.split-legend{display:flex;gap:24px;font-size:12px;color:var(--ink-soft);font-family:'IBM Plex Mono',monospace;letter-spacing:.06em}
.split-legend .dot{width:10px;height:10px;display:inline-block;margin-right:6px;vertical-align:middle}
.split-legend .dot.sk{background:var(--skincare)}
.split-legend .dot.mk{background:var(--makeup)}

.cat-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}
@media(max-width:680px){.cat-grid{grid-template-columns:1fr}}
.cat-card{background:var(--bg-card);border:1px solid var(--line);padding:24px;box-shadow:var(--shadow);border-left:4px solid var(--line)}
.cat-card.sk{border-left-color:var(--skincare);background:linear-gradient(180deg,var(--skincare-bg) 0%,var(--bg-card) 80px)}
.cat-card.mk{border-left-color:var(--makeup);background:linear-gradient(180deg,var(--makeup-bg) 0%,var(--bg-card) 80px)}
.cat-card h3{font-family:'Cormorant Garamond',serif;font-size:22px;font-style:italic;font-weight:500;margin-bottom:4px}
.cat-card.sk h3{color:var(--skincare)}
.cat-card.mk h3{color:var(--makeup)}
.cat-card .tag{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:18px}

.kw-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}
.kw-card{background:var(--bg-card);border:1px solid var(--line);padding:24px 22px;box-shadow:var(--shadow)}
.kw-card h3{font-family:'IBM Plex Sans KR';font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-mute);margin-bottom:14px;display:flex;justify-content:space-between;align-items:center}
.kw-card h3 .tot{font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--ink-mute);font-weight:400}
.kw-list{display:flex;flex-direction:column;gap:8px}
.kw-row{display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;padding:7px 0;border-bottom:1px dotted var(--line)}
.kw-row:last-child{border:0}
.kw-term{font-size:14px;font-weight:500;color:var(--ink)}
.kw-count{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--ink-mute);font-weight:500}
.kw-bar{grid-column:1/-1;height:2px;background:var(--line);margin-top:4px;position:relative;overflow:hidden}
.kw-bar::after{content:"";position:absolute;left:0;top:0;bottom:0;background:var(--accent);width:var(--w,0%)}
.kw-card.pos h3{color:var(--pos)}
.kw-card.pos .kw-bar::after{background:var(--pos)}
.kw-card.pos{background:linear-gradient(180deg,var(--pos-bg) 0%,var(--bg-card) 80px)}
.kw-card.neg h3{color:var(--neg)}
.kw-card.neg .kw-bar::after{background:var(--neg)}
.kw-card.neg{background:linear-gradient(180deg,var(--neg-bg) 0%,var(--bg-card) 80px)}
.kw-card.disc{background:linear-gradient(180deg,var(--accent-bg) 0%,var(--bg-card) 80px)}
.kw-card.disc h3{color:var(--accent)}
.kw-card.cat-sk .kw-bar::after{background:var(--skincare)}
.kw-card.cat-sk h3{color:var(--skincare)}
.kw-card.cat-mk .kw-bar::after{background:var(--makeup)}
.kw-card.cat-mk h3{color:var(--makeup)}

.prod-nav{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:32px;padding:16px 20px;background:var(--bg-card);border:1px solid var(--line);position:sticky;top:0;z-index:10;backdrop-filter:blur(8px);background:rgba(255,254,250,.92)}
.prod-nav button{font-family:'IBM Plex Sans KR';font-size:12px;background:transparent;border:1px solid var(--line);padding:7px 12px;cursor:pointer;color:var(--ink-soft);transition:all .15s;border-radius:2px;font-weight:500;display:flex;align-items:center;gap:6px}
.prod-nav button:hover{border-color:var(--ink);color:var(--ink)}
.prod-nav button.active{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.prod-nav button .star{color:var(--accent-soft);font-size:10px}
.prod-nav button .mku{font-size:9px;color:var(--makeup);font-weight:600;background:var(--makeup-bg);padding:1px 6px;border-radius:8px}
.prod-nav button.active .mku{color:var(--makeup);background:#fff}

.prod-detail{display:none}
.prod-detail.active{display:block}
.prod-head{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:flex-end;margin-bottom:28px;padding-bottom:24px;border-bottom:1px solid var(--ink)}
.prod-name{font-family:'Cormorant Garamond',serif;font-size:clamp(28px,4vw,42px);font-weight:500;line-height:1.05;letter-spacing:-.01em}
.prod-meta{text-align:right;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--ink-mute);line-height:1.8}
.prod-meta .rating{font-family:'Cormorant Garamond',serif;font-size:36px;color:var(--accent);font-weight:500}
.prod-meta .revwcnt{font-size:13px;color:var(--ink)}

/* product split bar (mini) */
.prod-split{background:var(--bg-card);border:1px solid var(--line);padding:18px 22px;margin-bottom:28px;box-shadow:var(--shadow)}
.prod-split-label{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:10px;font-family:'IBM Plex Mono',monospace;font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-mute)}
.prod-split-label em{font-family:'Cormorant Garamond',serif;font-style:italic;text-transform:none;font-size:13px;letter-spacing:0;color:var(--ink)}
.mini-bar{height:28px;display:flex;border:1px solid var(--line);background:#fff;overflow:hidden;border-radius:2px}
.mini-bar .sk{background:var(--skincare);color:#fff;display:flex;align-items:center;justify-content:flex-start;padding-left:12px;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;letter-spacing:.08em;transition:width .6s}
.mini-bar .mk{background:var(--makeup);color:#fff;display:flex;align-items:center;justify-content:flex-end;padding-right:12px;font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;letter-spacing:.08em;transition:width .6s}

.attr-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;margin-bottom:32px}
.attr-card{background:var(--bg-card);border:1px solid var(--line);padding:20px}
.attr-q{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-mute);font-family:'IBM Plex Mono',monospace;margin-bottom:4px}
.attr-iem{font-family:'Cormorant Garamond',serif;font-size:22px;font-weight:500;margin-bottom:14px;color:var(--ink)}
.attr-opt{display:grid;grid-template-columns:1fr auto;gap:6px;align-items:center;padding:4px 0;font-size:13px}
.attr-opt .lbl{color:var(--ink-soft)}
.attr-opt .pct{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--ink-mute);font-weight:500}
.attr-opt.max .lbl{font-weight:600;color:var(--ink)}
.attr-opt.max .pct{color:var(--accent);font-weight:600}
.attr-bar{grid-column:1/-1;height:3px;background:var(--line);margin-top:2px;position:relative}
.attr-bar::after{content:"";position:absolute;left:0;top:0;bottom:0;width:var(--w);background:var(--accent-soft)}
.attr-opt.max .attr-bar::after{background:var(--accent)}
.attr-n{font-family:'IBM Plex Mono',monospace;font-size:9.5px;letter-spacing:.08em;color:var(--ink-mute);margin-top:10px;padding-top:8px;border-top:1px dotted var(--line)}

.mini-sec-title{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--ink-mute);margin:30px 0 14px}

.quote-block{background:var(--neg-bg);border-left:3px solid var(--neg);padding:20px 22px;margin-top:24px}
.quote-block h4{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--neg);font-family:'IBM Plex Mono',monospace;margin-bottom:14px}
.quote{font-family:'Cormorant Garamond',serif;font-size:15px;font-style:italic;line-height:1.5;color:var(--ink);padding:8px 0;border-bottom:1px dotted rgba(168,67,58,.25)}
.quote:last-child{border:0}
.quote .star{font-family:'IBM Plex Mono',monospace;font-style:normal;font-size:10px;color:var(--neg);margin-right:10px;letter-spacing:.05em}

.insights{background:#1a1815;color:#f2ebdb;padding:48px 44px;margin:40px -20px -40px;position:relative}
.insights::before{content:"KEY INSIGHTS";position:absolute;top:-12px;left:44px;background:#1a1815;color:var(--accent-soft);padding:0 12px;font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.22em}
.insights h2{font-family:'Cormorant Garamond',serif;font-size:32px;font-weight:500;font-style:italic;margin-bottom:32px;color:#f2ebdb}
.insight-row{display:grid;grid-template-columns:48px 1fr;gap:20px;padding:18px 0;border-top:1px solid #3a342b}
.insight-row:first-of-type{border-top:1px solid #f2ebdb;padding-top:22px}
.insight-num{font-family:'Cormorant Garamond',serif;font-size:40px;color:var(--accent-soft);line-height:1;font-style:italic}
.insight-body h3{font-family:'IBM Plex Sans KR';font-size:15px;font-weight:600;margin-bottom:8px;color:#f2ebdb}
.insight-body p{font-size:13.5px;line-height:1.7;color:#c2b8a2}
.insight-body em{color:var(--accent-soft);font-style:normal;font-weight:500}

footer{margin-top:60px;padding-top:24px;border-top:1px solid var(--line);font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--ink-mute);letter-spacing:.08em;text-align:center;line-height:1.8}

@media(max-width:680px){
  body{padding:18px 14px 60px}
  .prod-head{grid-template-columns:1fr}
  .prod-meta{text-align:left}
  .insights{margin:40px -14px -40px;padding:32px 24px}
  .insights::before{left:24px}
  .split-bar{height:40px}
  .split-bar .sk, .split-bar .mk{font-size:16px}
}
</style>
</head>
<body>

<header class="masthead">
  <div class="eyebrow">
    <span>DAISO MALL · VOICE-OF-CUSTOMER DOSSIER</span>
    <span class="date">VOL. 02 — APR 2026</span>
  </div>
  <h1 class="title"><b>The Lab</b> <span>by Blanc Doux</span></h1>
  <div class="subtitle mono" style="font-size:13px;letter-spacing:.02em">고객 언어로 재구성한 브랜드·제품 포지셔닝 리포트</div>
  <div class="badgeline">
    <span class="badge accent">전수조사</span>
    <span class="badge">상품 <span id="s-prods"></span></span>
    <span class="badge">리뷰 <span id="s-revs"></span></span>
    <span class="badge v2">v2 · 키워드 병합 + 카테고리 분할</span>
  </div>
</header>

<div class="stats">
  <div class="stat"><div class="k">Total Products</div><div class="v" id="stat-prods"></div></div>
  <div class="stat"><div class="k">Total Reviews</div><div class="v" id="stat-revs"></div></div>
  <div class="stat"><div class="k">Avg Rating</div><div class="v" id="stat-rating"></div></div>
  <div class="stat"><div class="k">Skincare Share</div><div class="v" id="stat-skincare"></div></div>
</div>

<!-- SECTION 1 (NEW): Skincare vs Makeup -->
<section>
  <div class="section-head">
    <span class="section-num">§ 01</span>
    <h2>Skincare × Makeup</h2>
    <span class="meta">customer reaction split</span>
  </div>

  <div class="split-hero">
    <div class="splitline">
      고객은 이 브랜드를 <em id="hero-sk-share"></em>은 스킨케어로, <em id="hero-mk-share"></em>은 <em>메이크업 루틴의 일부</em>로 이야기한다.
    </div>
    <div class="split-bar">
      <div class="sk" id="hero-sk-bar"></div>
      <div class="mk" id="hero-mk-bar"></div>
    </div>
    <div class="split-legend">
      <span><span class="dot sk"></span>스킨케어 언급 <span id="hero-sk-cnt"></span></span>
      <span><span class="dot mk"></span>메이크업 언급 <span id="hero-mk-cnt"></span></span>
    </div>
  </div>

  <div class="cat-grid">
    <div class="cat-card sk">
      <h3>Skincare Vocabulary</h3>
      <div class="tag">기초 · 효능 · 피부 반응</div>
      <div class="kw-list" id="brand-skincare"></div>
    </div>
    <div class="cat-card mk">
      <h3>Makeup Vocabulary</h3>
      <div class="tag">화장 · 베이스 · 피부 위 반응</div>
      <div class="kw-list" id="brand-makeup"></div>
    </div>
  </div>
</section>

<!-- SECTION 2: Brand-level -->
<section>
  <div class="section-head">
    <span class="section-num">§ 02</span>
    <h2>Brand-level Signal</h2>
    <span class="meta">aggregated across 15 products</span>
  </div>

  <div class="kw-grid">
    <div class="kw-card disc">
      <h3>🔍 Discovery / Inflow<span class="tot">고객 유입 키워드</span></h3>
      <div class="kw-list" id="brand-disc"></div>
    </div>
    <div class="kw-card pos">
      <h3>😍 Positive Keywords<span class="tot">만족 키워드 Top 15</span></h3>
      <div class="kw-list" id="brand-pos"></div>
    </div>
    <div class="kw-card neg">
      <h3>😟 Complaint Patterns<span class="tot">불만·이탈 지점</span></h3>
      <div class="kw-list" id="brand-neg"></div>
    </div>
  </div>
</section>

<!-- SECTION 3: Product Deep-Dive -->
<section>
  <div class="section-head">
    <span class="section-num">§ 03</span>
    <h2>Product Deep-Dive</h2>
    <span class="meta">click to navigate · 메이크업 비중 표시</span>
  </div>

  <div class="prod-nav" id="prod-nav"></div>
  <div id="prod-container"></div>
</section>

<!-- SECTION 4: Insights -->
<section>
  <div class="insights">
    <h2>상품기획 관점 인사이트</h2>

    <div class="insight-row">
      <div class="insight-num">01</div>
      <div class="insight-body">
        <h3>고객의 21%는 이 브랜드를 "메이크업 제품"으로 말한다</h3>
        <p>전체 키워드 언급 중 <em>메이크업 관련 21.1% (3,544건)</em>. 특히 <em>틴티드 커버 크림 51.2%</em>, 옴므 톤커버 39.7%, 결광 스킨핏프렙 35.6%는 스킨케어보다 메이크업 언어로 소비된다. 제품 카테고리와 고객 인식의 어긋남 — 패키지·광고 카피를 "메이크업 전 수분막", "파데 대신 쓰는" 등 <em>use-case 기반 포지셔닝</em>으로 재설계할 기회.</p>
      </div>
    </div>

    <div class="insight-row">
      <div class="insight-num">02</div>
      <div class="insight-body">
        <h3>브랜드 삼위일체 = "촉촉 · 순함 · 가성비"</h3>
        <p>스킨케어 맥락 최다 언급: <em>촉촉 3,489 · 피부 1,455 · 수분 1,256 · 흡수 886 · 자극(없다) 782 · 순함 680</em>. 이 틀은 다이소 기초제품 카테고리 전반에 흔하므로 <em>브랜드 고유성은 없다</em>. 차별화는 사용 맥락 기반 라인 세분화(결광·옴므)에서 나온다.</p>
      </div>
    </div>

    <div class="insight-row">
      <div class="insight-num">03</div>
      <div class="insight-body">
        <h3>기대-성능 갭 = 건조 (353건)</h3>
        <p>주장 키워드는 "물광·히알·수분"인데 ★1~3 리뷰 최다 불만은 "건조"다. <em>겨울철·건성 타깃 속건조 대응 파생 SKU</em>(리치 버전, 나이트 크림, 부스팅 오일) 기회 존재.</p>
      </div>
    </div>

    <div class="insight-row">
      <div class="insight-num">04</div>
      <div class="insight-body">
        <h3>올리브영 비교 유입 ≈ 유튜브 유입</h3>
        <p>올영 비교 44건 ≈ 유튜브 47건. 다이소가 더 이상 "저가 채널"이 아니라 <em>"올영에서 쓰던 걸 가성비로 갈아타는 채널"</em>로 재정의되고 있다. 경쟁 구도 변화.</p>
      </div>
    </div>

    <div class="insight-row">
      <div class="insight-num">05</div>
      <div class="insight-body">
        <h3>저노출 히어로 후보 2종</h3>
        <p>결광 선에센스(168건/★4.7), 옴므 선크림(153건/★4.9)은 리뷰 수는 적지만 만족도·긍정 집중도 최상위. <em>프로모션·VMD 집중 투입할 확장 후보.</em></p>
      </div>
    </div>
  </div>
</section>

<footer>
  Data compiled 2026-04-22 · Source: daisomall.co.kr public reviews · Tokenizer: Kiwi · Keyword normalization: synonym merging · Category classification: curated skincare/makeup lexicon · For internal product planning use only
</footer>

<script>
const DATA = __DATA__;
const {products, brand} = DATA;

document.getElementById('s-prods').textContent = brand.total_products;
document.getElementById('s-revs').textContent = brand.total_reviews.toLocaleString();
document.getElementById('stat-prods').innerHTML = brand.total_products + '<small>SKU</small>';
document.getElementById('stat-revs').innerHTML = brand.total_reviews.toLocaleString() + '<small>건</small>';
const avgR = (products.reduce((s,p)=>s+parseFloat(p.avgRating),0)/products.length).toFixed(2);
document.getElementById('stat-rating').innerHTML = avgR + '<small>/ 5.0</small>';
document.getElementById('stat-skincare').innerHTML = brand.skincare_share + '<small>%</small>';

// Hero split
document.getElementById('hero-sk-share').textContent = brand.skincare_share + '%';
document.getElementById('hero-mk-share').textContent = brand.makeup_share + '%';
document.getElementById('hero-sk-bar').style.width = brand.skincare_share + '%';
document.getElementById('hero-sk-bar').textContent = brand.skincare_share + '% 스킨케어';
document.getElementById('hero-mk-bar').style.width = brand.makeup_share + '%';
document.getElementById('hero-mk-bar').textContent = '메이크업 ' + brand.makeup_share + '%';
document.getElementById('hero-sk-cnt').textContent = brand.skincare_total.toLocaleString() + '건';
document.getElementById('hero-mk-cnt').textContent = brand.makeup_total.toLocaleString() + '건';

function renderKwList(containerId, items, maxVal){
  const el = document.getElementById(containerId);
  const max = maxVal || Math.max(...items.map(i=>i[1]));
  el.innerHTML = items.map(([term, count])=>{
    const pct = (count/max*100).toFixed(1);
    return `<div class="kw-row">
      <span class="kw-term">${term}</span>
      <span class="kw-count">${count.toLocaleString()}</span>
      <span class="kw-bar" style="--w:${pct}%"></span>
    </div>`;
  }).join('');
}

renderKwList('brand-skincare', brand.top_skincare_brand.slice(0,12));
renderKwList('brand-makeup',   brand.top_makeup_brand.slice(0,12));
renderKwList('brand-disc',     brand.top_discovery_brand);
renderKwList('brand-pos',      brand.top_positive_brand.slice(0,15));
renderKwList('brand-neg',      brand.top_complaints_brand);

// Product navigation
const navEl = document.getElementById('prod-nav');
const container = document.getElementById('prod-container');

products.forEach((p, idx)=>{
  const btn = document.createElement('button');
  const short = p.pdNm.replace(/더랩 ?바이 ?블랑두 ?/,'').replace(/더랩바이블랑두 ?/,'').slice(0,22);
  btn.innerHTML = `${short}
    <span class="star">★${p.avgRating}</span>
    <span class="mku">MK ${p.makeup_pct}%</span>`;
  btn.onclick = ()=>selectProduct(idx);
  if(idx===0) btn.classList.add('active');
  navEl.appendChild(btn);

  const det = document.createElement('div');
  det.className = 'prod-detail' + (idx===0?' active':'');
  det.id = 'prod-'+idx;
  det.innerHTML = renderProduct(p);
  container.appendChild(det);
});

function selectProduct(idx){
  navEl.querySelectorAll('button').forEach((b,i)=>b.classList.toggle('active', i===idx));
  container.querySelectorAll('.prod-detail').forEach((d,i)=>d.classList.toggle('active', i===idx));
  window.scrollTo({top: container.offsetTop - 80, behavior:'smooth'});
}

function renderProduct(p){
  const attrHtml = (p.attributes||[]).map(a=>{
    const opts = [...a.options].sort((x,y)=>y.percent-x.percent);
    const maxP = opts[0].percent;
    return `<div class="attr-card">
      <div class="attr-q">${a.question||''}</div>
      <div class="attr-iem">${a.item}</div>
      ${opts.map(o=>`<div class="attr-opt ${o.percent===maxP?'max':''}">
        <span class="lbl">${o.label}</span>
        <span class="pct">${o.percent}%</span>
        <span class="attr-bar" style="--w:${o.percent}%"></span>
      </div>`).join('')}
      <div class="attr-n">n = ${a.total_responses?.toLocaleString()||'—'}</div>
    </div>`;
  }).join('');

  const maxSk = Math.max(1, ...p.skincare_keywords.map(k=>k.count));
  const maxMk = Math.max(1, ...p.makeup_keywords.map(k=>k.count));
  const maxPos = Math.max(1, ...p.positive_keywords.map(k=>k.count));
  const maxNeg = Math.max(1, ...p.complaint_patterns.map(k=>k.count), 1);
  const maxDisc = Math.max(1, ...p.discovery_mentions.map(k=>k.count), 1);

  const skHtml = p.skincare_keywords.slice(0,12).map(k=>`<div class="kw-row">
    <span class="kw-term">${k.term}</span>
    <span class="kw-count">${k.count.toLocaleString()}</span>
    <span class="kw-bar" style="--w:${(k.count/maxSk*100).toFixed(1)}%"></span>
  </div>`).join('') || '<div style="color:var(--ink-mute);font-size:13px">데이터 부족</div>';

  const mkHtml = p.makeup_keywords.slice(0,12).map(k=>`<div class="kw-row">
    <span class="kw-term">${k.term}</span>
    <span class="kw-count">${k.count.toLocaleString()}</span>
    <span class="kw-bar" style="--w:${(k.count/maxMk*100).toFixed(1)}%"></span>
  </div>`).join('') || '<div style="color:var(--ink-mute);font-size:13px">데이터 부족</div>';

  const posHtml = p.positive_keywords.slice(0,12).map(k=>`<div class="kw-row">
    <span class="kw-term">${k.term}</span>
    <span class="kw-count">${k.count.toLocaleString()}</span>
    <span class="kw-bar" style="--w:${(k.count/maxPos*100).toFixed(1)}%"></span>
  </div>`).join('');

  const negHtml = p.complaint_patterns.map(k=>`<div class="kw-row">
    <span class="kw-term">${k.label}</span>
    <span class="kw-count">${k.count.toLocaleString()}</span>
    <span class="kw-bar" style="--w:${(k.count/maxNeg*100).toFixed(1)}%"></span>
  </div>`).join('');

  const discHtml = p.discovery_mentions.map(k=>`<div class="kw-row">
    <span class="kw-term">${k.label}</span>
    <span class="kw-count">${k.count.toLocaleString()}</span>
    <span class="kw-bar" style="--w:${(k.count/maxDisc*100).toFixed(1)}%"></span>
  </div>`).join('');

  const samplesHtml = p.low_rating_sample.length ? `<div class="quote-block">
    <h4>★1~3 리뷰 샘플 — 이탈 지점의 생생한 언어</h4>
    ${p.low_rating_sample.slice(0,4).map(s=>`<div class="quote">
      <span class="star">★${s.score}</span>${(s.text||'').replace(/</g,'&lt;')}
    </div>`).join('')}
  </div>` : '';

  return `
  <div class="prod-head">
    <div class="prod-name">${p.pdNm}</div>
    <div class="prod-meta">
      pdNo · ${p.pdNo}<br>
      <span class="rating">★${p.avgRating}</span><br>
      <span class="revwcnt">${p.revwCnt.toLocaleString()} 리뷰</span>
    </div>
  </div>

  <div class="prod-split">
    <div class="prod-split-label">
      <span>고객 언어 분포</span>
      <em>스킨케어 ${p.skincare_pct}% · 메이크업 ${p.makeup_pct}%</em>
    </div>
    <div class="mini-bar">
      <div class="sk" style="width:${p.skincare_pct}%">${p.skincare_pct>18?'스킨케어 '+p.skincare_pct+'%':''}</div>
      <div class="mk" style="width:${p.makeup_pct}%">${p.makeup_pct>18?'메이크업 '+p.makeup_pct+'%':''}</div>
    </div>
  </div>

  ${attrHtml ? `<h3 class="mini-sec-title">Structured VOC · 고객이 직접 선택한 속성</h3>
  <div class="attr-grid">${attrHtml}</div>` : ''}

  <h3 class="mini-sec-title">Category Split · 스킨케어 vs 메이크업 언어</h3>
  <div class="cat-grid">
    <div class="cat-card sk">
      <h3>Skincare Words</h3>
      <div class="tag">${p.skincare_total.toLocaleString()}건 언급</div>
      <div class="kw-list">${skHtml}</div>
    </div>
    <div class="cat-card mk">
      <h3>Makeup Words</h3>
      <div class="tag">${p.makeup_total.toLocaleString()}건 언급</div>
      <div class="kw-list">${mkHtml}</div>
    </div>
  </div>

  <h3 class="mini-sec-title">Sentiment & Discovery · 만족·불만·유입</h3>
  <div class="kw-grid">
    <div class="kw-card disc">
      <h3>🔍 Discovery / Inflow<span class="tot">왜 알게·샀나</span></h3>
      <div class="kw-list">${discHtml || '<div style="color:var(--ink-mute);font-size:13px">데이터 부족</div>'}</div>
    </div>
    <div class="kw-card pos">
      <h3>😍 Positive<span class="tot">★5 과다 출현</span></h3>
      <div class="kw-list">${posHtml}</div>
    </div>
    <div class="kw-card neg">
      <h3>😟 Complaints<span class="tot">정규식 패턴</span></h3>
      <div class="kw-list">${negHtml || '<div style="color:var(--ink-mute);font-size:13px">데이터 부족</div>'}</div>
    </div>
  </div>

  ${samplesHtml}
  `;
}
</script>
</body></html>
'''

# Need to re-attach attributes since products_sorted in v2 lost them
attrs = json.load(open('attrs_by_product.json','r',encoding='utf-8'))
for p in products:
    p['attributes'] = attrs.get(p['pdNo'], {}).get('attributes', [])

data_js = json.dumps({"products": products, "brand": brand}, ensure_ascii=False)
html = HTML.replace('__DATA__', data_js)
import os
os.makedirs('/mnt/user-data/outputs', exist_ok=True)
out = '/mnt/user-data/outputs/daiso_blancdoux_voc_dashboard.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Saved: {out} ({len(html):,} bytes)")
