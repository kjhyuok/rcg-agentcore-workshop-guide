"""
Phase 3 아키텍처 다이어그램 생성 (AWS 아이콘)
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.ml import Bedrock
from diagrams.aws.compute import Lambda
from diagrams.aws.management import Cloudwatch
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with Diagram(
    "Phase 3: Multi-Agent + Evaluations",
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

    with Cluster("Multi-Agent Orchestration", graph_attr={"style": "rounded", "bgcolor": "#f3e5f5"}):
        orchestrator = Bedrock("Orchestrator Agent\n(사전 배포)\n의도 분류 → 라우팅")

    with Cluster("참가자 Agent (Phase 1~2에서 배포)", graph_attr={"bgcolor": "#fff3e0"}):
        a1 = Bedrock("추천 Agent\n(Phase 1)")
        a2 = Bedrock("CS Agent\n(Phase 2A)")
        a3 = Bedrock("수요예측 Agent\n(Phase 2B)")

    with Cluster("Evaluations (LLM-as-Judge)", graph_attr={"bgcolor": "#e8f5e9"}):
        eval_agent = Bedrock("품질 평가\nHelpfulness\nAccuracy\nTool Selection")
        score = Cloudwatch("종합 점수\n→ 발표 & 시상")

    orchestrator >> Edge(label="상품 추천", color="#e65100") >> a1
    orchestrator >> Edge(label="CS 문의", color="#1565c0") >> a2
    orchestrator >> Edge(label="재고/발주", color="#2e7d32") >> a3

    a1 >> Edge(style="dashed", color="#388e3c") >> eval_agent
    a2 >> Edge(style="dashed", color="#388e3c") >> eval_agent
    a3 >> Edge(style="dashed", color="#388e3c") >> eval_agent
    eval_agent >> Edge(label="점수 산출", color="#388e3c") >> score
