"""
Phase 2A 아키텍처 다이어그램 생성 (AWS 아이콘)
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.ml import Bedrock
from diagrams.aws.compute import Lambda
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import WAF as Shield
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with Diagram(
    "Phase 2A: CS Agent + Memory + Browser",
    filename=os.path.join(OUTPUT_DIR, "phase2a_architecture"),
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
            agent = Bedrock("CS Agent\n(Strands SDK)\nClaude Sonnet 4.6")

        with Cluster("Memory", graph_attr={"bgcolor": "#e8eaf6"}):
            memory = Bedrock("AgentCore Memory\n고객 선호/이력·대화 요약\nNamespace 분리")

        with Cluster("Gateway (CS Tools)", graph_attr={"bgcolor": "#e3f2fd"}):
            t1 = Lambda("lookup\n_order")
            t2 = Lambda("return\n_policy")
            t3 = Lambda("process\n_return")
            t4 = Lambda("delivery\n_status")

        with Cluster("Browser Tool", graph_attr={"bgcolor": "#e0f2f1"}):
            browser = Bedrock("Mock 경쟁사 사이트\n가격 비교\n프로모션 수집")

        with Cluster("Policy Engine", graph_attr={"bgcolor": "#fce4ec"}):
            policy = Shield("환불 > 50,000원\n→ 에스컬레이션")

        obs = Cloudwatch("Observability")

    agent >> Edge(label="retrieve", color="#3f51b5") >> memory
    agent >> Edge(label="MCP", color="#1565c0") >> t1
    agent >> Edge(color="#1565c0") >> t2
    agent >> Edge(color="#1565c0") >> t3
    agent >> Edge(color="#1565c0") >> t4
    agent >> Edge(label="웹 탐색", color="#00695c") >> browser
    agent >> Edge(label="행동 체크", color="#c62828") >> policy
    agent >> Edge(style="dashed", color="#6a1b9a") >> obs
