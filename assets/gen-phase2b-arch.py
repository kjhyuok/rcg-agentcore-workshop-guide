"""
Phase 2B 아키텍처 다이어그램 생성 (AWS 아이콘)
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.ml import Bedrock
from diagrams.aws.compute import Lambda
from diagrams.aws.management import Cloudwatch
from diagrams.aws.database import Dynamodb as DynamoDB
from diagrams.aws.security import WAF as Shield
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

with Diagram(
    "Phase 2B: 수요예측 Agent + Memory + Browser",
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
            agent = Bedrock("Demand Agent\n(Strands SDK)\nClaude Sonnet 4.6")

        with Cluster("Memory", graph_attr={"bgcolor": "#e8eaf6"}):
            memory = DynamoDB("발주 이력/패턴\n/orders/{actorId}/")

        with Cluster("Gateway (Demand Tools)", graph_attr={"bgcolor": "#e3f2fd"}):
            t1 = Lambda("inventory\n_status")
            t2 = Lambda("sales\n_trend")
            t3 = Lambda("external\n_factors")
            t4 = Lambda("purchase\n_order")

        with Cluster("Browser Tool", graph_attr={"bgcolor": "#e0f2f1"}):
            browser = Bedrock("Mock 뉴스/날씨\n트렌드 기사 수집\n기온/강수량 확인")

        with Cluster("Policy Engine", graph_attr={"bgcolor": "#fce4ec"}):
            policy = Shield("발주 > 500,000원\n→ 점장 승인")

        obs = Cloudwatch("Observability")

    agent >> Edge(label="retrieve", color="#3f51b5") >> memory
    agent >> Edge(label="MCP", color="#1565c0") >> t1
    agent >> Edge(color="#1565c0") >> t2
    agent >> Edge(color="#1565c0") >> t3
    agent >> Edge(color="#1565c0") >> t4
    agent >> Edge(label="트렌드/날씨", color="#00695c") >> browser
    agent >> Edge(label="발주 승인", color="#c62828") >> policy
    agent >> Edge(style="dashed", color="#6a1b9a") >> obs
