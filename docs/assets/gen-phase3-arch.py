"""
Phase 3 아키텍처 다이어그램 생성 (AWS 아이콘)

주의: Phase 3가 "바이브코딩으로 나만의 Agent 만들기"로 재구성되어 새 아키텍처를 반영했습니다.
PNG 재생성 필요 시: pip install diagrams && python3 gen-phase3-arch.py
(현재 가이드 index.md는 mermaid만 사용 — PNG는 선택적)
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.ml import Bedrock
from diagrams.aws.compute import Lambda
from diagrams.aws.management import Cloudwatch
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with Diagram(
    "Phase 3: 나만의 Agent (Runtime + Gateway + Memory)",
    filename=os.path.join(OUTPUT_DIR, "phase3_architecture"),
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
            agent = Bedrock("My Agent\n(바이브코딩으로 구현)\nClaude Sonnet 4.6")

        with Cluster("Gateway (Tool 팔레트 7개)", graph_attr={"bgcolor": "#e3f2fd"}):
            t1 = Lambda("Phase 1 Tools\ncustomer/product\n/history")
            t2 = Lambda("내 트랙 Tools\n(2A: cs_* /\n2B: demand_*)")

        with Cluster("Built-in Tools (선택)", graph_attr={"bgcolor": "#e0f2f1"}):
            ci = Bedrock("Code Interpreter\n계산/시각화")
            browser = Bedrock("Browser\n뉴스/날씨/가격")

        with Cluster("Memory (Step 4 연동)", graph_attr={"bgcolor": "#e8eaf6"}):
            memory = Bedrock("AgentCore Memory\n기억의 주체 = actor_id\n(고객 ID / 매장 ID)")

        obs = Cloudwatch("Observability")

    agent >> Edge(label="MCP", color="#1565c0") >> t1
    agent >> Edge(color="#1565c0") >> t2
    agent >> Edge(style="dashed", label="선택", color="#00695c") >> ci
    agent >> Edge(style="dashed", color="#00695c") >> browser
    agent >> Edge(label="retrieve/save", color="#3f51b5") >> memory
    agent >> Edge(style="dashed", color="#6a1b9a") >> obs
