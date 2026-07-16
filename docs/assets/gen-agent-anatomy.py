"""
Agent 구성 개념도 생성 (Agent = Model + System Prompt + Tools via Gateway)
실행: .venv/bin/python docs/assets/gen-agent-anatomy.py
출력: docs/assets/agent-anatomy.png
graphviz(dot) 필요 — PATH에 /opt/homebrew/bin 포함해서 실행
"""
import os
import subprocess

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent-anatomy")

# 워크샵 톤(주황/시안/보라)에 맞춘 개념 조립도.
# Agent라는 하나의 상자가 Model + System Prompt + Tools 세 재료로 조립되고,
# Tools는 Gateway(MCP)를 통해 Lambda 3종에서 공급됨을 보여준다.
DOT = r"""
digraph AgentAnatomy {
  rankdir=LR;
  bgcolor="white";
  pad="0.4";
  fontname="Helvetica";
  node [fontname="Helvetica", fontsize=13, shape=box, style="rounded,filled", penwidth=1.2];
  edge [fontname="Helvetica", fontsize=11, color="#64748b", penwidth=1.4];

  // Agent 조립 결과
  agent [label="🤖 Agent", fillcolor="#0d9488", fontcolor="white", fontsize=18, width=1.8, height=1.0, penwidth=2];

  // 3가지 재료
  subgraph cluster_parts {
    label="Agent = Model + System Prompt + Tools";
    fontsize=15;
    fontcolor="#334155";
    style="rounded,dashed";
    color="#94a3b8";
    labelloc="t";
    margin=16;

    model  [label="🧠 Model\n\nClaude Sonnet 4.6\n추론·판단하는 두뇌", fillcolor="#ede9fe", color="#7c3aed", fontcolor="#4c1d95"];
    prompt [label="📋 System Prompt\n\n행동 규칙\n(Tool 호출 순서·제약)", fillcolor="#dbeafe", color="#2563eb", fontcolor="#1e3a8a"];
    tools  [label="🔧 Tools\n\nAgent가 쓸 수 있는 도구\n(Gateway가 공급)", fillcolor="#ffedd5", color="#ea580c", fontcolor="#7c2d12"];
  }

  // Gateway → Tools 공급 계층
  subgraph cluster_gw {
    label="Gateway (MCP Protocol)";
    fontsize=13;
    fontcolor="#0e7490";
    style="rounded,filled";
    fillcolor="#ecfeff";
    color="#22d3ee";
    labelloc="t";
    margin=14;

    l1 [label="λ customer_profile", fillcolor="#fff7ed", color="#fdba74", fontcolor="#7c2d12", fontsize=11];
    l2 [label="λ product_search",   fillcolor="#fff7ed", color="#fdba74", fontcolor="#7c2d12", fontsize=11];
    l3 [label="λ purchase_history", fillcolor="#fff7ed", color="#fdba74", fontcolor="#7c2d12", fontsize=11];
  }

  // 조립 화살표 (재료 → Agent)
  model  -> agent [color="#7c3aed"];
  prompt -> agent [color="#2563eb"];
  tools  -> agent [color="#ea580c"];

  // Gateway가 Tools를 공급 (MCP)
  l1 -> tools [style=dashed, color="#0e7490", label="MCP", fontcolor="#0e7490"];
  l2 -> tools [style=dashed, color="#0e7490"];
  l3 -> tools [style=dashed, color="#0e7490"];
}
"""

src = OUTPUT + ".dot"
with open(src, "w") as f:
    f.write(DOT)

subprocess.run(
    ["dot", "-Tpng", "-Gdpi=150", src, "-o", OUTPUT + ".png"],
    check=True,
)
os.remove(src)
print(f"생성 완료: {OUTPUT}.png")
