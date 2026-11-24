#!/usr/bin/env python3
"""생활비 물가 연구소 (life-money-lab) — 100% 무료 매일 자동 갱신 SEO·쿠팡 수익 사이트 빌더."""
from __future__ import annotations

import html
import json
import math
import os
import shutil
import ssl
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
KST = timezone(timedelta(hours=9))
NOW = datetime.now(KST)

SITE_NAME = "생활비 물가 연구소"
SITE_URL = "https://0520goeus.github.io/life-money-lab"
PRICE_NOTE_URL = "https://0520goeus.github.io/price-note"
ELEC_CALC_URL = "https://0520goeus.github.io/elec-calc"
BLOGGER_URL = "https://lifefixnote-kr.blogspot.com"
INDEXNOW_KEY = "a4d91f72c3084b5ea7f6d9218c340e12"
GOOGLE_FILE = "google873809343766a3b6.html"
COUPANG_TRACKING = "AF9170267"
COUPANG_WIDGET_ID = 1049499

DISCLOSURE = "이 페이지는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."
COUPANG_WIDGET = (
    '<section class="card shop">'
    f'<p class="disc">{DISCLOSURE}</p>'
    '<h3>지금 많이 찾는 생활 절약·인기 상품</h3>'
    '<script src="https://ads-partners.coupang.com/g.js"></script>'
    f'<script>new PartnersCoupang.G({{"id":{COUPANG_WIDGET_ID},"template":"carousel",'
    f'"trackingCode":"{COUPANG_TRACKING}","width":"100%","height":"140","tsource":""}});</script>'
    "</section>"
)

TARIFF_NORMAL = [(200, 910, 120.0), (400, 1600, 214.6), (999999, 7300, 307.3)]
TARIFF_SUMMER = [(300, 910, 120.0), (450, 1600, 214.6), (999999, 7300, 307.3)]


def _ssl_ctx():
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def fetch_json(url: str):
    req = Request(url, headers={"User-Agent": "LifeMoneyLab/1.0"})
    with urlopen(req, timeout=20, context=_ssl_ctx()) as resp:
        return json.loads(resp.read().decode("utf-8"))


def esc(v) -> str:
    return html.escape(str(v or ""), quote=True)


def won(n) -> str:
    return f"{int(round(n)):,}원"


def calc_bill(kwh: float, month: int) -> int:
    tiers = TARIFF_SUMMER if month in (7, 8) else TARIFF_NORMAL
    base_fee, energy, prev = tiers[0][1], 0.0, 0.0
    for lim, bf, rate in tiers:
        if kwh > prev:
            base_fee = bf
            energy += (min(kwh, lim) - prev) * rate
            prev = lim
    sub = math.floor(base_fee + energy + 14.0 * kwh)
    vat = int(sub * 0.10 + 0.5)
    fund = math.floor(sub * 0.027 / 10) * 10
    return math.floor((sub + vat + fund) / 10) * 10


def svg_bars(title: str, rows: list[tuple[str, int, int, str]]) -> str:
    w, top, rh = 720, 48, 56
    h = top + len(rows) * rh + 24
    mx = max((max(a, b) for _, a, b, _ in rows), default=1) or 1
    out = []
    for i, (name, v1, v2, unit) in enumerate(rows):
        y = top + i * rh
        w1 = max(6, int(v1 / mx * 330))
        w2 = max(6, int(v2 / mx * 330))
        out.append(
            f'<text x="14" y="{y+16}" fill="#0f172a" font-size="13.5" font-weight="700">{esc(name[:24])}</text>'
            f'<rect x="14" y="{y+22}" width="{w1}" height="10" rx="5" fill="#94a3b8"/>'
            f'<text x="{22+w1}" y="{y+31}" fill="#475569" font-size="11.5">{v1:,}{unit}</text>'
            f'<rect x="14" y="{y+36}" width="{w2}" height="10" rx="5" fill="#e11d48"/>'
            f'<text x="{22+w2}" y="{y+45}" fill="#be123c" font-size="11.5" font-weight="700">{v2:,}{unit}</text>'
        )
    return (
        f'<figure class="chart-box"><svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{esc(title)}">'
        f'<text x="14" y="26" fill="#0f172a" font-size="16" font-weight="800">{esc(title)}</text>{"".join(out)}'
        "</svg><figcaption>회색: 이전·최저 기준 / 빨강: 최근·최고 기준 (자동 생성 실측 그래프)</figcaption></figure>"
    )


CSS = """
:root{--bg:#f8fafc;--card:#ffffff;--ink:#0f172a;--sub:#475569;--line:#e2e8f0;--accent:#2563eb;--up:#e11d48;--down:#059669}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.75 -apple-system,"Apple SD Gothic Neo",sans-serif}
header{background:#0f172a;color:#fff;padding:18px 20px}
header .wrap{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
header a{color:#e2e8f0;text-decoration:none;font-size:14px;font-weight:600}
header .brand{font-size:19px;font-weight:800;color:#fff}
nav{display:flex;gap:14px;flex-wrap:wrap}
.wrap{max-width:920px;margin:0 auto;padding:0 18px}
main{padding:28px 0 60px;display:grid;gap:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px}
h1{font-size:28px;line-height:1.3;margin:0 0 10px;letter-spacing:-.02em}
h2{font-size:20px;margin:0 0 12px}h3{font-size:17px;margin:0 0 8px}
.lede{color:var(--sub);margin:0 0 8px}.date{font-size:13px;color:var(--accent);font-weight:700;margin:0 0 6px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}
.tile{display:grid;gap:6px;padding:16px;border:1px solid var(--line);border-radius:12px;background:#fff;text-decoration:none;color:var(--ink)}
.tile:hover{border-color:var(--accent)}
.tile b{font-size:16px}.tile small{color:var(--sub)}
.up{color:var(--up);font-weight:700}.down{color:var(--down);font-weight:700}
.tbl-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14.5px}
th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left;white-space:normal}
thead th{background:#f1f5f9;font-size:13px;color:var(--sub)}
.chart-box{margin:16px 0;padding:14px;border:1px solid var(--line);border-radius:12px;background:#f8fafc}
figcaption{font-size:12px;color:var(--sub);margin-top:6px}
.shop .disc{font-size:12.5px;color:var(--sub);margin:0 0 10px}
.faq{padding:14px;background:#f8fafc;border-left:4px solid #0f172a;border-radius:8px;margin:10px 0}
.faq p{margin:4px 0}
footer{border-top:1px solid var(--line);padding:24px 0 44px;color:var(--sub);font-size:13.5px}
footer a{color:var(--accent);text-decoration:none}
"""


def render_page(rel: str, title: str, desc: str, body: str, json_ld: dict | None = None) -> str:
    ld_html = f'<script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False)}</script>' if json_ld else ""
    canon = f"{SITE_URL}/{rel}" if rel != "index.html" else f"{SITE_URL}/"
    page_html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:locale" content="ko_KR">
<link rel="stylesheet" href="{SITE_URL}/style.css">
{ld_html}
<meta name="google-site-verification" content="E0MKLI_9g0wTNR9pjNKmxb_QGiA51AIK93dV9qBKumg"><script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8749404731911210" crossorigin="anonymous"></script><script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"생활비 물가 연구소","url":"https://0520goeus.github.io/life-money-lab/"}}</script>
</head>
<body>
<header><div class="wrap">
  <a class="brand" href="{SITE_URL}/">{SITE_NAME}</a>
  <nav>
    <a href="{SITE_URL}/rise-report.html">물가 급등 TOP 15</a>
    <a href="{SITE_URL}/gap-report.html">2배 가격격차</a>
    <a href="{SITE_URL}/drop-report.html">최저가 포착</a>
    <a href="{SITE_URL}/elec-report.html">전기세 비교</a>
    <a href="{PRICE_NOTE_URL}/" rel="noopener">해뎐 가격노트</a>
    <a href="{ELEC_CALC_URL}/" rel="noopener">전기세 얼마</a>
  </nav>
</div></header>
<main class="wrap">{body}<div style="margin:20px auto;max-width:960px;padding:16px 20px;border-radius:14px;background:linear-gradient(135deg,#0f172a,#0f766e);color:#fff;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;"><div><div style="font-weight:800;font-size:16px;">2026 직장인·1인셀러 무매크로 자동계산 엑셀 3종 올인원 번들</div><div style="font-size:13px;opacity:.9;margin-top:2px;">1인셀러 마진·ROAS + 내집마련 매물10개 비교 + 월급 가계부·순자산 대시보드 (즉시 다운로드)</div></div><a href="https://0520goeus.github.io/excel-store/" target="_blank" rel="noopener" style="background:#facc15;color:#0f172a;padding:10px 18px;border-radius:10px;font-weight:800;font-size:14px;text-decoration:none;white-space:nowrap;">3종 번들 즉시 다운로드 →</a></div>
</main>
<footer><div class="wrap">
  <p>매일 자동 업데이트 ({NOW.strftime("%Y-%m-%d %H:%M")} KST) · 데이터 출처: 한국소비자원 생필품 가격정보 / 한국전력공사 주택용 요금표</p>
  <p>패밀리 사이트: <a href="{PRICE_NOTE_URL}/">해뎐 가격노트</a> · <a href="{ELEC_CALC_URL}/">전기세 얼마</a> · <a href="https://0520goeus.github.io/vs-pick/">가성비 VS 비교 사전</a> · <a href="https://0520goeus.github.io/life-fee-calc/">가전용량·직구관세</a> · <a href="https://0520goeus.github.io/money-calc-kr/">연봉 실수령액</a> · <a href="https://0520goeus.github.io/benefit-calc-kr/">지원금·실업급여</a> · <a href="https://0520goeus.github.io/seller-margin-calc/">셀러 마진 계산기</a> · <a href="{BLOGGER_URL}/">생활해결 노트</a></p>
</div><div style="margin:14px auto 8px;max-width:960px;display:flex;flex-wrap:wrap;gap:6px;justify-content:center;font-size:12px;"><a href="https://0520goeus.github.io/house-calc-kr/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">부동산·대출·복비</a><a href="https://0520goeus.github.io/car-calc-kr/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">자동차세·유지비</a><a href="https://0520goeus.github.io/money-calc-kr/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">실수령액·금융</a><a href="https://0520goeus.github.io/benefit-calc-kr/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">2026 지원금</a><a href="https://0520goeus.github.io/life-fee-calc/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">평수가전·직구관세</a><a href="https://0520goeus.github.io/elec-calc/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">전기세 계산기</a><a href="https://0520goeus.github.io/vs-pick/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">가성비 VS 124종</a><a href="https://0520goeus.github.io/price-note/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">588 생필품 시세</a><a href="https://0520goeus.github.io/seller-margin-calc/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">셀러마진·엑셀</a><a href="https://0520goeus.github.io/kr-trend-brief/" style="padding:4px 9px;border-radius:6px;background:rgba(148,163,184,.18);color:inherit;text-decoration:none;">실시간 트렌드</a></div>
</footer>
</body></html>"""
    out_path = DIST / rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(page_html, encoding="utf-8")
    return canon


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "style.css").write_text(CSS, encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / GOOGLE_FILE).write_text(f"google-site-verification: {GOOGLE_FILE}", encoding="utf-8")
    (DIST / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    (DIST / "ads.txt").write_text("google.com, pub-8749404731911210, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")

    # Fetch live data from sibling GitHub repos (0원)
    meta = fetch_json("https://raw.githubusercontent.com/0520goeus/price-note/main/data/meta.json")
    ref = fetch_json("https://raw.githubusercontent.com/0520goeus/price-note/main/data/ref.json")
    goods_raw = fetch_json("https://raw.githubusercontent.com/0520goeus/price-note/main/data/goods.json")
    appliances_raw = fetch_json("https://raw.githubusercontent.com/0520goeus/elec-calc/main/appliances.json")

    day = meta.get("day") or NOW.strftime("%Y-%m-%d")
    items = []
    for gid, g in goods_raw.items():
        h = g.get("history") or []
        if len(h) < 2:
            continue
        r = ref.get("goods", {}).get(gid, {})
        name = (r.get("name") or "").strip()
        if not name:
            continue
        cur_avg, cur_min, cur_max, cur_n = h[-1][1:5]
        base_avg = h[max(0, len(h) - 6)][1]
        if cur_avg <= 0 or base_avg <= 0 or cur_n < 10:
            continue
        trend_pct = (cur_avg - base_avg) / base_avg * 100.0
        gap_ratio = (cur_max / cur_min) if cur_min > 0 else 1.0
        items.append({
            "id": gid,
            "name": name,
            "cat": r.get("top") or "생필품",
            "cls": r.get("cls") or "",
            "cur": int(cur_avg),
            "base": int(base_avg),
            "min": int(cur_min),
            "max": int(cur_max),
            "n": int(cur_n),
            "trend_pct": round(trend_pct, 1),
            "gap_won": int(cur_max - cur_min),
            "gap_ratio": round(gap_ratio, 2),
            "url": f"{PRICE_NOTE_URL}/p/{gid}.html",
        })

    rises = sorted(items, key=lambda x: x["trend_pct"], reverse=True)[:15]
    drops = sorted(items, key=lambda x: x["trend_pct"])[:15]
    gaps = sorted([x for x in items if x["min"] >= 800], key=lambda x: (x["gap_ratio"], x["gap_won"]), reverse=True)[:15]

    base_250 = calc_bill(250, NOW.month)
    elecs = []
    for a in appliances_raw:
        w = a["watts"][len(a["watts"]) // 2]
        duty = 0.65 if a.get("cycle") else 1.0
        kwh = round(w * a["hours"] * a["days"] * duty / 1000.0, 1)
        add_won = calc_bill(250 + kwh, NOW.month) - base_250
        elecs.append({**a, "w_mid": w, "kwh": kwh, "add_won": add_won, "url": f"{ELEC_CALC_URL}/a/{a['slug']}/"})
    elecs.sort(key=lambda x: x["add_won"], reverse=True)

    urls: list[str] = []

    def goods_table(rows):
        trs = "".join(
            f'<tr><td><a href="{r["url"]}" target="_blank" rel="noopener"><strong>{esc(r["name"])}</strong></a><br><small>{esc(r["cat"])} · {r["n"]}곳 조사</small></td>'
            f'<td>{won(r["base"])}</td><td><b>{won(r["cur"])}</b></td>'
            f'<td class="down">{won(r["min"])}</td><td class="up">{won(r["max"])}</td>'
            f'<td class="{"up" if r["trend_pct"]>0 else "down"}">{r["trend_pct"]:+.1f}%</td></tr>'
            for r in rows
        )
        return (
            '<div class="tbl-wrap"><table><thead><tr><th>품목명 (상세 차트)</th><th>이전 평균</th><th>최근 평균</th>'
            f'<th>전국 최저</th><th>전국 최고</th><th>변동률</th></tr></thead><tbody>{trs}</tbody></table></div>'
        )

    # 1. Rise report
    faqs_rise = [
        (f"{day} 기준 가격이 가장 많이 오른 생필품은?", f"{rises[0]['name']}이(가) 최근 평균 {won(rises[0]['cur'])}으로 {rises[0]['trend_pct']:+.1f}% 상승했습니다."),
        ("오른 생필품을 싸게 사는 방법은?", f"같은 품목도 최저가 매장({won(rises[0]['min'])})과 최고가 매장({won(rises[0]['max'])}) 격차가 크므로 온라인 묶음가와 비교 후 구매하는 것이 유리합니다."),
    ]
    urls.append(render_page(
        "rise-report.html",
        f"[{day}] 마트 물가 급등 생필품 TOP 15 실측 리포트 | {SITE_NAME}",
        f"{day} 한국소비자원 588품목 실측 기준 가장 크게 오른 생필품 TOP 15 평균가·최저가 비교표.",
        f'<section class="card"><p class="date">{day} 한국소비자원 실측</p><h1>최근 가격 급등 생필품 TOP 15</h1>'
        f'<p class="lede">전국 매장 실제 판매가 기준, 최근 상승 폭이 가장 큰 15개 품목을 자동 집계했습니다. 각 품목을 누르면 <a href="{PRICE_NOTE_URL}/">해뎐 가격노트</a>의 주간 그래프를 바로 볼 수 있습니다.</p>'
        f'{svg_bars("물가 급등 상위 6개 품목 (이전 평균 vs 최근 평균)", [(r["name"], r["base"], r["cur"], "원") for r in rises[:6]])}'
        f'{goods_table(rises)}</section>{COUPANG_WIDGET}'
        f'<section class="card"><h2>자주 묻는 질문</h2>' + "".join(f'<div class="faq"><p><b>Q. {esc(q)}</b></p><p>A. {esc(a)}</p></div>' for q, a in faqs_rise) + "</section>",
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs_rise]},
    ))

    # 2. Gap report
    urls.append(render_page(
        "gap-report.html",
        f"[{day}] 같은 제품인데 매장별 2배 차이? 생필품 가격 격차 TOP 15 | {SITE_NAME}",
        f"같은 생필품인데 편의점·마트·최저가 매장별 가격 차이가 가장 큰 TOP 15 실측 비교표.",
        f'<section class="card"><p class="date">{day} 전국 매장 비교</p><h1>같은 제품인데 2배 차이? 가격 격차 TOP 15</h1>'
        f'<p class="lede">최저가와 최고가 격차가 가장 큰 품목입니다. 모르고 정가로 사면 한 번 장볼 때 수천 원씩 손해 볼 수 있습니다.</p>'
        f'{svg_bars("최저가 vs 최고가 격차 TOP 6", [(r["name"], r["min"], r["max"], "원") for r in gaps[:6]])}'
        f'{goods_table(gaps)}</section>{COUPANG_WIDGET}',
    ))

    # 3. Drop report
    urls.append(render_page(
        "drop-report.html",
        f"[{day}] 지금 사면 이득! 가격 하락·최저가 생필품 TOP 15 | {SITE_NAME}",
        f"한국소비자원 최신 조사 기준 가격이 가장 크게 내린 생필품 TOP 15와 전국 최저가 정리.",
        f'<section class="card"><p class="date">{day} 알뜰 장보기 경보</p><h1>가격 확 떨어진 생필품 TOP 15</h1>'
        f'<p class="lede">최근 몇 주 사이 평균 판매가가 가장 크게 하락한 생필품 목록입니다. 비축 구매 전 기준 가격으로 활용하세요.</p>'
        f'{svg_bars("가격 하락 상위 6개 품목", [(r["name"], r["base"], r["cur"], "원") for r in drops[:6]])}'
        f'{goods_table(drops)}</section>{COUPANG_WIDGET}',
    ))

    # 4. Elec report
    elec_trs = "".join(
        f'<tr><td><a href="{e["url"]}" target="_blank" rel="noopener"><strong>{esc(e["name"])}</strong></a><br><small>{esc(e["cat"])}</small></td>'
        f'<td>{e["w_mid"]:,}W</td><td>하루 {e["hours"]}시간</td><td>{e["kwh"]} kWh</td>'
        f'<td class="up">+{won(e["add_won"])}</td></tr>'
        for e in elecs[:15]
    )
    urls.append(render_page(
        "elec-report.html",
        f"[{NOW.year}년 {NOW.month}월] 전기세 많이 나오는 가전 TOP 15 — 한전 누진제 실계산 | {SITE_NAME}",
        f"{NOW.month}월 한전 주택용 저압 누진제 기준, 가전 15종의 한 달 추가 전기요금 순위표.",
        f'<section class="card"><p class="date">{NOW.year}년 {NOW.month}월 한전 요금표 기준</p><h1>전기세 많이 나오는 가전 TOP 15</h1>'
        f'<p class="lede">평소 월 250kWh를 쓰는 가구가 각 가전을 추가 사용할 때 늘어나는 전기요금입니다. 우리 집 정확한 계산은 <a href="{ELEC_CALC_URL}/">전기세 얼마 계산기</a>에서 바로 해볼 수 있습니다.</p>'
        f'{svg_bars("월 추가 전기요금 TOP 6 (기본 250kWh 가구)", [(e["name"], int(e["add_won"]*0.35), e["add_won"], "원") for e in elecs[:6]])}'
        f'<div class="tbl-wrap"><table><thead><tr><th>가전제품 (개별 계산기)</th><th>대표 소비전력</th><th>사용 패턴</th><th>월 전력량</th><th>월 추가요금</th></tr></thead><tbody>{elec_trs}</tbody></table></div>'
        f'</section>{COUPANG_WIDGET}',
    ))

    # 5. Category long-tail SEO pages
    cats: dict[str, list[dict]] = {}
    for it in items:
        cats.setdefault(it["cat"], []).append(it)
    cat_tiles = []
    for idx, (cat_name, c_items) in enumerate(sorted(cats.items(), key=lambda kv: -len(kv[1]))[:8], start=1):
        c_slug = f"cat-{idx}.html"
        c_sorted = sorted(c_items, key=lambda x: x["trend_pct"], reverse=True)
        urls.append(render_page(
            c_slug,
            f"[{day}] {cat_name} 가격 비교 ({len(c_items)}개 품목) — 최저가·변동률 | {SITE_NAME}",
            f"{cat_name} {len(c_items)}개 생필품의 전국 평균가·최저가·최고가 비교표 ({day} 실측).",
            f'<section class="card"><p class="date">{day} 실측 · {len(c_items)}개 품목</p><h1>{esc(cat_name)} 가격 비교 리포트</h1>'
            f'<p class="lede">{esc(cat_name)} 카테고리의 전국 매장 가격 흐름을 정리했습니다.</p>'
            f'{goods_table(c_sorted[:30])}</section>{COUPANG_WIDGET}',
        ))
        cat_tiles.append(f'<a class="tile" href="{SITE_URL}/{c_slug}"><b>{esc(cat_name)}</b><small>{len(c_items)}개 품목 실측 비교 →</small></a>')

    # 6. Homepage
    home_body = f"""
    <section class="card">
      <p class="date">{day} 자동 집계 완료 · 588개 생필품 + 24종 가전</p>
      <h1>오늘의 생활비·물가·전기세 핵심 리포트</h1>
      <p class="lede">한국소비자원 공식 생필품 가격과 한전 누진제 요금표를 매일 자동 분석해 장보기·전기요금 절약 포인트를 정리합니다.</p>
      <div class="grid">
        <a class="tile" href="{SITE_URL}/rise-report.html"><span class="up">▲ +{rises[0]['trend_pct']:.1f}%</span><b>물가 급등 TOP 15</b><small>1위 {esc(rises[0]['name'][:18])}</small></a>
        <a class="tile" href="{SITE_URL}/gap-report.html"><span class="up">{gaps[0]['gap_ratio']:.1f}배 격차</span><b>매장별 가격 격차 TOP 15</b><small>최대 {won(gaps[0]['gap_won'])} 차이</small></a>
        <a class="tile" href="{SITE_URL}/drop-report.html"><span class="down">▼ {abs(drops[0]['trend_pct']):.1f}%</span><b>가격 하락 최저가 TOP 15</b><small>1위 {esc(drops[0]['name'][:18])}</small></a>
        <a class="tile" href="{SITE_URL}/elec-report.html"><span class="up">+{won(elecs[0]['add_won'])}/월</span><b>전기세 폭탄 가전 TOP 15</b><small>1위 {esc(elecs[0]['name'])}</small></a>
      </div>
    </section>
    {COUPANG_WIDGET}
    <section class="card">
      <h2>카테고리별 물가 리포트</h2>
      <div class="grid">{"".join(cat_tiles)}</div>
    </section>
    <section class="card">
      <h2>무료 생활 절약 도구 모음</h2>
      <div class="grid">
        <a class="tile" href="{PRICE_NOTE_URL}/"><b>해뎐 가격노트</b><small>588개 생필품 주간 가격 그래프 조회 →</small></a>
        <a class="tile" href="{ELEC_CALC_URL}/"><b>전기세 얼마 계산기</b><small>가전 24종 우리 집 누진세 실시간 계산 →</small></a>
        <a class="tile" href="{BLOGGER_URL}/"><b>생활해결 노트 블로그</b><small>생활 실무·절약 가이드 아카이브 →</small></a>
      </div>
    </section>
    """
    urls.insert(0, render_page(
        "index.html",
        f"{SITE_NAME} | 생필품 물가 급등·최저가·전기세 절약 자동 리포트",
        f"{day} 기준 한국소비자원 588개 생필품 물가 순위와 한전 누진제 가전 전기요금 비교 리포트.",
        home_body,
    ))

    # Sitemap, Robots, RSS, urls.txt
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"<url><loc>{u}</loc><lastmod>{NOW.strftime('%Y-%m-%d')}</lastmod></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (DIST / "urls.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")
    rss_items = "".join(
        f"<item><title>{esc(r['name'])} {won(r['cur'])} ({r['trend_pct']:+.1f}%)</title>"
        f"<link>{SITE_URL}/rise-report.html</link><guid isPermaLink='false'>rise-{r['id']}-{day}</guid></item>"
        for r in rises[:10]
    )
    (DIST / "rss.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{SITE_NAME}</title>'
        f"<link>{SITE_URL}/</link><description>매일 자동 갱신되는 한국 생필품 물가·전기세 절약 리포트</description>{rss_items}</channel></rss>",
        encoding="utf-8",
    )
    print(f"생활비 물가 연구소 빌드 완료: {len(urls)}페이지 ({day})")


if __name__ == "__main__":
    main()
