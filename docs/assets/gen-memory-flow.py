"""
Memory 연동 흐름 개념도 생성 (Phase 2A Step 3)
패턴: Memory 조회 → 프롬프트 주입 → Agent 실행 → 대화 기록 저장
실행: .venv/bin/python docs/assets/gen-memory-flow.py
출력: docs/assets/memory-flow.png
graphviz(dot) 필요 — PATH에 /opt/homebrew/bin 포함해서 실행
"""
import os
import subprocess

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory-flow")

# gen-agent-anatomy.py와 같은 워크샵 톤(주황/시안/보라/틸).
# 상태 없는 Phase 1 Agent와 대비되는 "기억하는 Agent"의 4단계 흐름:
#   ① fetch_customer_context (retrieve_memory_records) — 이전 맥락 조회
#   ② 프롬프트에 맥락 주입
#   ③ Agent 실행
#   ④ save_turn (create_event) — 이번 대화 저장
# AgentCore Memory가 ①(읽기)과 ④(쓰기) 양쪽에 연결됨을 보여준다.
DOT = r"""
digraph MemoryFlow {
  rankdir=LR;
  bgcolor="white";
  pad="0.4";
  fontname="Helvetica";
  node [fontname="Helvetica", fontsize=13, shape=box, style="rounded,filled", penwidth=1.2];
  edge [fontname="Helvetica", fontsize=11, color="#64748b", penwidth=1.4];

  // AgentCore Memory 저장소 (읽기/쓰기 양쪽 연결)
  memory [label="🧠 AgentCore Memory\n\n고객 선호·이력\n대화 요약\n(actor_id로 격리)", fillcolor="#ede9fe", color="#7c3aed", fontcolor="#4c1d95", fontsize=13, width=2.0];

  // 4단계 파이프라인
  subgraph cluster_flow {
    label="매 요청마다: 조회 → 주입 → 실행 → 저장";
    fontsize=14;
    fontcolor="#334155";
    style="rounded,dashed";
    color="#94a3b8";
    labelloc="t";
    margin=16;

    step1 [label="① 맥락 조회\n\nfetch_customer_context()\nretrieve_memory_records", fillcolor="#ecfeff", color="#0e7490", fontcolor="#155e75"];
    step2 [label="② 프롬프트 주입\n\n이전 맥락을\nsystem prompt에 결합", fillcolor="#dbeafe", color="#2563eb", fontcolor="#1e3a8a"];
    step3 [label="③ Agent 실행\n\nagent(message,\ncontext=context)", fillcolor="#dcfce7", color="#16a34a", fontcolor="#14532d"];
    step4 [label="④ 대화 저장\n\nsave_turn()\ncreate_event", fillcolor="#ffedd5", color="#ea580c", fontcolor="#7c2d12"];
  }

  // 파이프라인 순서
  step1 -> step2 [color="#334155"];
  step2 -> step3 [color="#334155"];
  step3 -> step4 [color="#334155"];

  // Memory ↔ 조회/저장 연결
  memory -> step1 [label="read", color="#0e7490", fontcolor="#0e7490"];
  step4 -> memory [label="write", color="#ea580c", fontcolor="#ea580c"];
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
