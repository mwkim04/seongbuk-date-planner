"""
실데이터 품질 진단 스크립트
===========================

배포된 app.py의 실제 수집/분류/필터 로직을 그대로 사용해, 카카오 API에서
수집한 진짜 장소 데이터에 품질 문제가 있는지 검사합니다.

이 스크립트는 합성 데이터가 아니라 **실제 카카오 데이터**를 검사하므로,
"존재하지 않는/이상한 주소", "데이트에 부적합한 업종이 추천 후보에 남았는지",
"좌표가 지역 범위를 벗어났는지" 등을 실제로 잡아낼 수 있습니다.

사용법
------
1. app.py와 같은 폴더에 이 파일을 둡니다(이미 같은 폴더에 있습니다).
2. .env 파일에 KAKAO_REST_API_KEY를 설정하거나, 환경변수로 키를 넣습니다.
3. 터미널에서 실행:

   python diagnose_data.py                # 기본: 모든 지역, 술집 제외
   python diagnose_data.py --region 안암동 # 특정 지역만
   python diagnose_data.py --include-bar  # 술집 포함해서 검사
   python diagnose_data.py --report quality.html  # HTML 리포트로 저장

주의
----
- 실제 카카오 API를 호출하므로 호출 한도를 사용합니다(지역당 약 100~130회).
- 키가 코드/깃에 노출되지 않도록 .env 또는 환경변수만 사용하세요.
"""

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

# app.py의 함수들을 그대로 재사용 (수집/분류/필터 로직 중복 없이 검증)
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

try:
    from dotenv import load_dotenv
    env_path = APP_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except Exception:
    pass


def _get_key() -> str:
    return os.getenv("KAKAO_REST_API_KEY", "").strip()


def _import_app():
    """app.py를 import하되, Streamlit UI 실행부는 건너뛰도록 안전하게 로드."""
    import importlib.util
    import types

    # Streamlit이 import 시점에 페이지를 그리지 않도록 가벼운 무력화는 어렵기 때문에,
    # app.py의 상단 로직 부분만 별도 네임스페이스로 실행한다.
    src = (APP_DIR / "app.py").read_text(encoding="utf-8")
    lines = src.splitlines()
    try:
        cut = next(i for i, l in enumerate(lines) if l.startswith("with st.sidebar"))
    except StopIteration:
        cut = len(lines)

    # streamlit/folium 등 UI 의존성은 더미로 대체
    class _Noop:
        def __call__(self, *a, **k):
            return None

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def __getattr__(self, n):
            return _Noop()

    class _SessionState(dict):
        def __getattr__(self, k):
            return self.get(k)

        def __setattr__(self, k, v):
            self[k] = v

        def __delattr__(self, k):
            self.pop(k, None)

    class _ST:
        def __init__(self):
            self.session_state = _SessionState()

        def cache_data(self, *a, **k):
            def deco(f):
                return f
            return deco

        cache_resource = cache_data

        def set_page_config(self, *a, **k):
            pass

        def __getattr__(self, n):
            return _Noop()

    sys.modules.setdefault("streamlit", _ST())
    for name in ["folium", "streamlit_folium", "docx", "dotenv"]:
        if name not in sys.modules:
            m = types.ModuleType(name)
            if name == "streamlit_folium":
                m.st_folium = lambda *a, **k: None
            if name == "docx":
                m.Document = object
            if name == "dotenv":
                m.load_dotenv = lambda *a, **k: None
            sys.modules[name] = m

    ns = {"__name__": "app_logic", "__file__": str(APP_DIR / "app.py")}
    exec("\n".join(lines[:cut]), ns)
    return ns


def diagnose_region(ns, region: str, include_bar: bool):
    """한 지역의 실제 수집 결과를 검사."""
    collect = ns["collect_places"]
    in_region = ns["is_in_selected_region"]
    is_non_date = ns["is_non_date_place"]
    hav = ns["haversine_km"]
    REGION_CENTERS = ns["REGION_CENTERS"]

    api_key = _get_key()
    if not api_key:
        raise SystemExit("KAKAO_REST_API_KEY가 없습니다. .env 또는 환경변수에 키를 설정하세요.")

    df = collect(region, include_bar, api_key, [])
    issues = []
    type_counts = Counter()
    center = REGION_CENTERS.get(region)

    if df.empty:
        return {"region": region, "n": 0, "issues": ["수집된 장소가 0건"], "types": {}, "rows": []}

    for _, row in df.iterrows():
        name = str(row.get("name", ""))
        addr = str(row.get("address", ""))
        lat, lon = row.get("lat"), row.get("lon")
        ptype = row.get("type")
        url = str(row.get("url", ""))
        cost = row.get("cost", 0)
        type_counts[ptype] += 1

        # 1) 주소 유효성: 비었거나 '서울'이 없는 주소
        if not addr or "서울" not in addr:
            issues.append(f"[주소이상] {name} → '{addr}'")
        # 2) 좌표가 지역 범위 밖 (필터를 통과했는데도 멀리 있는 경우)
        if center:
            clat, clon, rad = center
            try:
                if hav((clat, clon), (float(lat), float(lon))) > rad + 0.1:
                    issues.append(f"[좌표이탈] {name} → 중심에서 {hav((clat,clon),(float(lat),float(lon))):.1f}km")
            except Exception:
                issues.append(f"[좌표오류] {name} → lat={lat}, lon={lon}")
        # 3) 데이트 부적합 업종이 남아있는지 (필터 누락 검사)
        if is_non_date(name, str(row.get("category_name", "")), addr):
            issues.append(f"[부적합업종 누락] {name} ({row.get('category_name','')})")
        # 4) 술집 제외인데 술집이 남았는지
        if ptype == "술집" and not include_bar:
            issues.append(f"[술집누출] {name}")
        # 5) URL/비용 sanity
        if not url.startswith("http"):
            issues.append(f"[링크이상] {name} → '{url}'")
        if not (0 <= int(cost) <= 80000):
            issues.append(f"[비용이상] {name} → {cost}원")
        # 6) 분류가 '기타'인데 남아있는지 (정상 흐름이면 제거됐어야 함)
        if ptype == "기타":
            issues.append(f"[미분류 잔존] {name}")

    return {
        "region": region,
        "n": len(df),
        "issues": issues,
        "types": dict(type_counts),
        "rows": df.to_dict("records"),
    }


def main():
    ap = argparse.ArgumentParser(description="성북구 데이트 플래너 실데이터 품질 진단")
    ap.add_argument("--region", default=None, help="검사할 지역(미지정 시 전체)")
    ap.add_argument("--include-bar", action="store_true", help="술집 포함해서 검사")
    ap.add_argument("--report", default=None, help="HTML 리포트 저장 경로(예: quality.html)")
    args = ap.parse_args()

    ns = _import_app()
    regions = [args.region] if args.region else list(ns["REGION_KEYWORDS"].keys())

    results = []
    total_n = total_issues = 0
    print("=" * 64)
    print("실데이터 품질 진단 시작")
    print("=" * 64)
    for region in regions:
        print(f"\n▶ {region} 수집 중...", flush=True)
        res = diagnose_region(ns, region, args.include_bar)
        results.append(res)
        total_n += res["n"]
        total_issues += len(res["issues"])
        print(f"  수집 {res['n']}건 · 타입 {res['types']}")
        if res["issues"]:
            print(f"  ⚠️ 발견된 문제 {len(res['issues'])}건:")
            for it in res["issues"][:20]:
                print("     -", it)
            if len(res["issues"]) > 20:
                print(f"     ... 외 {len(res['issues'])-20}건")
        else:
            print("  ✅ 문제 없음 — 모든 장소가 품질 검사 통과")

    print("\n" + "=" * 64)
    print(f"총 수집 {total_n}건 · 총 문제 {total_issues}건")
    print("=" * 64)

    if args.report:
        _write_html(results, total_n, total_issues, args.report)
        print(f"\nHTML 리포트 저장: {args.report}")


def _write_html(results, total_n, total_issues, path):
    rows_html = []
    for r in results:
        issues = "".join(f"<li>{i}</li>" for i in r["issues"]) or "<li class='ok'>✅ 문제 없음</li>"
        types = ", ".join(f"{k} {v}" for k, v in r["types"].items())
        rows_html.append(
            f"<section><h3>{r['region']} <small>({r['n']}건 · {types})</small></h3>"
            f"<ul>{issues}</ul></section>"
        )
    verdict = "✅ 합격 — 발견된 품질 문제 없음" if total_issues == 0 else f"⚠️ {total_issues}건의 품질 문제 발견"
    html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>실데이터 품질 진단</title>
<style>
body{{font-family:system-ui,'Apple SD Gothic Neo',sans-serif;max-width:880px;margin:0 auto;padding:40px 24px;color:#3a2c33;background:#fff6fa;line-height:1.6}}
h1{{color:#e23b86}} .verdict{{font-size:20px;font-weight:700;padding:18px 22px;border-radius:16px;background:#fff;border:2px solid #ffe0ec;margin-bottom:24px}}
section{{background:#fff;border:2px solid #ffe0ec;border-radius:16px;padding:18px 22px;margin-bottom:16px}}
h3{{color:#e23b86;margin-bottom:8px}} small{{color:#8a7480;font-weight:400}}
ul{{margin:0;padding-left:18px}} li{{font-size:14px;color:#a23}} li.ok{{color:#1f9d6b;list-style:none;margin-left:-18px}}
.meta{{color:#8a7480;font-size:14px;margin-bottom:20px}}
</style></head><body>
<h1>💝 실데이터 품질 진단 리포트</h1>
<div class="meta">실제 카카오 API 수집 데이터 기준 · 총 {total_n}건 검사</div>
<div class="verdict">{verdict}</div>
{''.join(rows_html)}
</body></html>"""
    Path(path).write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
