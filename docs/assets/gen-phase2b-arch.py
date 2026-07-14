"""
Phase 2B 아키텍처 다이어그램 생성 (AWS 아이콘)

주의: Phase 2B가 "뉴스/날씨 수집 Agent"로 재구성되어 새 아키텍처를 반영했습니다.
PNG 재생성 필요 시: pip install diagrams && python3 gen-phase2b-arch.py
(현재 가이드 index.md는 mermaid만 사용 — PNG는 선택적)
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.ml import Bedrock
from diagrams.aws.compute import Lambda
from diagrams.aws.management import Cloudwatch
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with Diagram(
    "Phase 2B: 뉴스/날씨 수집 Agent (Gateway + Browser)",
    filename=os.path.join(OUTPUT_DIR, "phase2b_architecture"),
    show=False,
    direction="TB",
    graph_attr={
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
        "dpi": "150",
    },
    node_attr={"fontsize": "10"},
    edge_attr={"fontsize": "9"},
):

    with Cluster("AgentCore Platform", graph_attr={"style": "rounded", "bgcolor": "#fff8e1"}):

        with Cluster("Runtime", graph_attr={"bgcolor": "#fff3e0"}):
            agent = Bedrock("Collector Agent\n(Strands SDK)\nClaude Sonnet 4.6")

        with Cluster("Gateway (Data Tools)", graph_attr={"bgcolor": "#e3f2fd"}):
            t1 = Lambda("inventory\n_status")
            t2 = Lambda("sales\n_trend")
            t3 = Lambda("external\n_factors")
            t4 = Lambda("purchase\n_order")

        with Cluster("Browser Tool", graph_attr={"bgcolor": "#e0f2f1"}):
            browser = Bedrock("Mock 뉴스/날씨\nweather-forecast.html\ntrend-news.html")

        obs = Cloudwatch("Observability")

    agent >> Edge(label="MCP", color="#1565c0") >> t1
    agent >> Edge(color="#1565c0") >> t2
    agent >> Edge(label="날씨/이벤트", color="#1565c0") >> t3
    agent >> Edge(color="#1565c0") >> t4
    agent >> Edge(label="실시간 수집", color="#00695c") >> browser
    agent >> Edge(style="dashed", color="#6a1b9a") >> obs
