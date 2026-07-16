"""
Phase 1 아키텍처 다이어그램 생성 (AWS 아이콘)
실행: python3 docs/assets/gen-phase1-arch.py
출력: docs/assets/phase1_architecture.png
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.ml import Bedrock
from diagrams.aws.compute import Lambda
from diagrams.aws.management import Cloudwatch
from diagrams.custom import Custom
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with Diagram(
    "Phase 1: 추천 Agent",
    filename=os.path.join(OUTPUT_DIR, "phase1_architecture"),
    show=False,
    direction="TB",
    graph_attr={
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
        "dpi": "150",
    },
    node_attr={"fontsize": "11"},
    edge_attr={"fontsize": "9"},
):

    with Cluster("AgentCore Platform", graph_attr={"style": "rounded", "bgcolor": "#fff8e1"}):

        with Cluster("Runtime (HTTPS Endpoint)", graph_attr={"bgcolor": "#fff3e0"}):
            agent = Bedrock("Agent\n(Strands SDK)\nClaude Sonnet 4.6")

        with Cluster("Gateway (MCP Protocol)", graph_attr={"bgcolor": "#e3f2fd"}):
            t1 = Lambda("customer\n_profile")
            t2 = Lambda("product\n_search")
            t3 = Lambda("purchase\n_history")

        obs = Cloudwatch("Observability\nGenAI Dashboard\n+ X-Ray Trace")

    agent >> Edge(label="MCP tool_use", color="#1565c0") >> t1
    agent >> Edge(color="#1565c0") >> t2
    agent >> Edge(color="#1565c0") >> t3
    agent >> Edge(label="자동 Trace", style="dashed", color="#6a1b9a") >> obs
