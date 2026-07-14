"""
Lambda: rcg-workshop-demand-external-factors
Tool 이름: external_factors

매장 운영에 영향을 주는 외부 요인(날씨 예보, 지역 이벤트, 공휴일)을 반환합니다.
Mock 데이터 — 워크샵 실습용.

Input Schema:
  store_id (string, required): 매장 ID (예: store-001)
  forecast_days (integer, optional): 향후 며칠간 (기본 7)

배포: python3.12, handler=index.handler, timeout=30s, memory=128MB
"""

import json
from datetime import datetime, timedelta


# --- Mock 데이터 ---

def _generate_weather_forecast(days: int) -> list:
    """향후 N일간 날씨 예보 생성 (Mock)"""
    base_date = datetime.now()
    patterns = [
        {"condition": "맑음", "high": 35, "low": 26, "humidity": 45, "precipitation": 0},
        {"condition": "맑음 (폭염주의보)", "high": 37, "low": 28, "humidity": 40, "precipitation": 0},
        {"condition": "맑음", "high": 36, "low": 27, "humidity": 42, "precipitation": 0},
        {"condition": "구름 많음", "high": 33, "low": 25, "humidity": 55, "precipitation": 10},
        {"condition": "소나기", "high": 30, "low": 24, "humidity": 75, "precipitation": 60},
        {"condition": "흐림", "high": 31, "low": 24, "humidity": 65, "precipitation": 30},
        {"condition": "맑음", "high": 34, "low": 26, "humidity": 48, "precipitation": 5},
    ]

    forecast = []
    for i in range(days):
        date = base_date + timedelta(days=i + 1)
        pattern = patterns[i % len(patterns)]
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day_of_week": ["월", "화", "수", "목", "금", "토", "일"][date.weekday()],
            **pattern,
        })
    return forecast


def _get_local_events(store_id: str, days: int) -> list:
    """지역 이벤트/공휴일 (Mock)"""
    base_date = datetime.now()

    events = [
        {
            "name": "여름 지역 축제",
            "date_start": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "date_end": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "type": "축제",
            "expected_visitors": 5000,
            "impact": "매장 반경 500m 내 대규모 인파 예상. 간편식/음료 수요 증가 가능.",
        },
        {
            "name": "초등학교 방학 시작",
            "date_start": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
            "date_end": None,
            "type": "시즌",
            "expected_visitors": None,
            "impact": "오전 시간대 가족 고객 증가. 간식/아이스크림류 수요 상승 예상.",
        },
    ]

    # days 범위 내의 이벤트만 필터 (Mock이라 항상 반환)
    return events[:2] if days >= 3 else events[:1]


def _get_alerts(store_id: str) -> list:
    """날씨 특보/경보 (Mock)"""
    return [
        {
            "type": "폭염주의보",
            "severity": "주의",
            "period": "내일~모레",
            "message": "낮 최고기온 35도 이상. 냉방용품/음료 수요 급증 가능.",
        }
    ]


# --- Handler ---

def handler(event, context):
    """
    AgentCore Gateway → MCP → 이 Lambda를 호출합니다.
    event 구조: {"store_id": "store-001", "forecast_days": 7}
    """
    # 파라미터 파싱
    body = event if isinstance(event, dict) else json.loads(event.get("body", "{}"))
    store_id = body.get("store_id", "store-001")
    forecast_days = body.get("forecast_days", 7)

    # 범위 제한
    forecast_days = max(1, min(forecast_days, 14))

    # Mock 데이터 조합
    weather = _generate_weather_forecast(forecast_days)
    events = _get_local_events(store_id, forecast_days)
    alerts = _get_alerts(store_id)

    result = {
        "store_id": store_id,
        "forecast_days": forecast_days,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "weather_forecast": weather,
        "local_events": events,
        "weather_alerts": alerts,
        "summary": _build_summary(weather, events, alerts),
    }

    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False),
    }


def _build_summary(weather: list, events: list, alerts: list) -> str:
    """사람이 읽기 쉬운 요약 (Agent가 이것만 읽어도 판단 가능)"""
    lines = []

    # 날씨 요약
    max_temp = max(d["high"] for d in weather)
    rainy_days = [d for d in weather if d["precipitation"] >= 50]
    if max_temp >= 35:
        lines.append(f"향후 {len(weather)}일 중 폭염(35도↑) 예상. 음료/빙과류 수요 증가 가능.")
    if rainy_days:
        days_str = ", ".join(d["date"] + "(" + d["day_of_week"] + ")" for d in rainy_days)
        lines.append(f"비 예보: {days_str}. 우산/우비 수요 가능, 외출 감소로 배달 주문 증가 예상.")

    # 이벤트 요약
    for ev in events:
        lines.append(f"[{ev['type']}] {ev['name']} ({ev['date_start']}~) — {ev['impact']}")

    # 경보 요약
    for alert in alerts:
        lines.append(f"⚠️ {alert['type']}({alert['severity']}): {alert['message']}")

    return " | ".join(lines) if lines else "특이사항 없음."
