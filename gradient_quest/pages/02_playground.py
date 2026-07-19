"""Playground — Watch a computation graph come to life, step by step.

Forward pass: values start at 0 and update live as each node is computed.
Backprop: gradients start at 0, output seed = 1, then flow backward with the chain rule.
"""

import streamlit as st
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.value import Value
from visualization.graph import draw_graph, trace
from visualization.forward_pass import get_topo_order, node_formula
from visualization.backprop import generate_backprop_steps, get_node_colors_at_step, COLORS

st.set_page_config(page_title="Playground | Gradient Quest", page_icon="🧮", layout="wide")
from game.ui import setup_chrome
setup_chrome()

st.markdown("""
<style>
    .legend { display: flex; gap: 14px; flex-wrap: wrap; margin: 10px 0; font-size: 0.88rem; }
    .legend span { padding: 4px 12px; border-radius: 12px; border: 1px solid rgba(128,128,128,0.3); }
    .info-strip {
        padding: 12px 18px; border-radius: 12px; margin: 10px 0; font-weight: 600;
        border: 1px solid #1cb0f6; background: rgba(28,176,246,0.10); color: #1cb0f6;
    }
    .info-done { border-color: #58cc02; background: rgba(88,204,2,0.10); color: #58cc02; }
</style>
""", unsafe_allow_html=True)

st.title("🧮 Playground")
st.caption("Build a computation graph, then watch it come alive — forward and backward.")

# ── Preset expressions ──
PRESETS = {
    "Simple: c = a × b": "a = Value(2, label='a')\nb = Value(3, label='b')\nc = a * b\nc.label = 'c'",
    "Chained: d = a×b + 1": "a = Value(2, label='a')\nb = Value(3, label='b')\nc = a * b\nc.label = 'c'\nd = c + 1\nd.label = 'd'",
    "Neuron: tanh(w·x + b)": "w = Value(0.5, label='w')\nx = Value(2, label='x')\nb = Value(1, label='b')\nwx = w * x\nwx.label = 'wx'\nz = wx + b\nz.label = 'z'\no = z.tanh()\no.label = 'o'",
    "Squared: y = x²": "x = Value(3, label='x')\ny = x * x\ny.label = 'y'",
}

preset = st.selectbox("📝 Pick a preset or edit below", list(PRESETS.keys()))
code = st.text_area("Expression", value=PRESETS[preset], height=150, key=f"code_{preset}")

# Build graph fresh each render (so gradients start at 0 before backprop plays)
namespace = {"Value": Value, "__builtins__": {}}
root = None
try:
    exec(code, namespace)  # noqa: S102
    value_vars = {k: v for k, v in namespace.items() if isinstance(v, Value) and k != "Value"}
    if value_vars:
        root = list(value_vars.values())[-1]
except Exception as e:
    st.error(f"Error in expression: {e}")

if root is None:
    st.warning("Define at least one Value to build a graph.")
    st.stop()

SPEED_MAP = {"🐢 Slow": 1.6, "🚶 Normal": 0.9, "🐇 Fast": 0.4}


def speed_slider(key):
    return SPEED_MAP[st.select_slider(
        "Animation speed", options=list(SPEED_MAP.keys()),
        value="🚶 Normal", key=key,
    )]


# ── Tabs for the 3 modes ──
tab_graph, tab_fwd, tab_bwd = st.tabs(["🌳 Graph", "▶️ Forward Pass", "🔄 Backprop"])

# ══════════════════════════════════════════════════════════════
# TAB 1: Static reference graph with formulas + value list
# ══════════════════════════════════════════════════════════════
with tab_graph:
    st.markdown("The full graph with every node's value and **how it was computed**.")
    nodes, _ = trace(root)
    formula_map = {id(n): node_formula(n) for n in nodes}
    st.graphviz_chart(draw_graph(root, formula_map=formula_map).source)

    st.subheader("🔍 How each value was computed")
    for n in get_topo_order(root):
        f = node_formula(n)
        if f:
            st.markdown(f"- **{n.label or 'node'}** = {f}")
        else:
            st.markdown(f"- **{n.label or 'input'}** = {n.data:.2f}  *(given input)*")

# ══════════════════════════════════════════════════════════════
# TAB 2: Forward pass — values start at 0, update live
# ══════════════════════════════════════════════════════════════
with tab_fwd:
    st.markdown("Every node starts at **0**. Watch values fill in as we compute from inputs → output.")
    speed = speed_slider("fwd_speed")
    topo = get_topo_order(root)

    if st.button("▶️ Play Forward Pass", type="primary", key="play_fwd"):
        graph_ph = st.empty()
        info_ph = st.empty()

        # Frame 0: everything is 0
        data_map = {id(n): 0.0 for n in topo}
        colors = {id(n): COLORS["unvisited"] for n in topo}
        graph_ph.graphviz_chart(draw_graph(root, node_colors=colors, data_map=data_map).source)
        info_ph.markdown('<div class="info-strip">All values initialized to 0. Starting forward pass…</div>', unsafe_allow_html=True)
        time.sleep(speed)

        formula_map = {}
        for idx, node in enumerate(topo):
            data_map[id(node)] = node.data
            f = node_formula(node)
            if f:
                formula_map[id(node)] = f
            colors = {}
            for j, n in enumerate(topo):
                if j < idx:
                    colors[id(n)] = COLORS["computed"]
                elif j == idx:
                    colors[id(n)] = COLORS["active"]
                else:
                    colors[id(n)] = COLORS["unvisited"]
            graph_ph.graphviz_chart(
                draw_graph(root, node_colors=colors, data_map=data_map, formula_map=formula_map).source
            )
            if f:
                info_ph.markdown(f'<div class="info-strip">Step {idx+1}: compute <b>{node.label or "node"}</b> = {f}</div>', unsafe_allow_html=True)
            else:
                info_ph.markdown(f'<div class="info-strip">Step {idx+1}: input <b>{node.label or "node"}</b> = {node.data:.2f} (given)</div>', unsafe_allow_html=True)
            time.sleep(speed)

        info_ph.markdown(f'<div class="info-strip info-done">✅ Forward pass complete! Output = {root.data:.3f}</div>', unsafe_allow_html=True)
    else:
        data_map = {id(n): 0.0 for n in topo}
        st.graphviz_chart(draw_graph(root, data_map=data_map).source)
        st.caption("Press play to run the forward pass — all values start at 0.")

    st.markdown('<div class="legend"><span>🔵 Not computed (0)</span><span>🟠 Computing now</span><span>🟢 Done</span></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 3: Backprop — grads start 0, output = 1, flow backward
# ══════════════════════════════════════════════════════════════
with tab_bwd:
    st.markdown("Every gradient starts at **0**. We seed the output with **grad = 1**, then apply the chain rule backward.")
    speed_b = speed_slider("bwd_speed")
    steps = generate_backprop_steps(root)   # runs backward(); node.grad now populated
    topo = get_topo_order(root)
    reverse_topo = list(reversed(topo))

    if st.button("🔄 Play Backpropagation", type="primary", key="play_bwd"):
        graph_ph = st.empty()
        info_ph = st.empty()

        # Data stays at final forward values throughout backprop
        data_map = {id(n): n.data for n in topo}

        # Frame 0: all grads 0
        grad_map = {id(n): 0.0 for n in topo}
        colors = {id(n): COLORS["unvisited"] for n in topo}
        graph_ph.graphviz_chart(draw_graph(root, node_colors=colors, data_map=data_map, grad_map=grad_map).source)
        info_ph.markdown('<div class="info-strip">All gradients start at 0.</div>', unsafe_allow_html=True)
        time.sleep(speed_b)

        # Reveal grads output-first
        formula_map = {}
        for idx, node in enumerate(reverse_topo):
            grad_map[id(node)] = node.grad
            step = steps[idx]
            formula_map[id(node)] = step["formula"]
            colors = get_node_colors_at_step(steps, idx + 1)
            graph_ph.graphviz_chart(
                draw_graph(root, node_colors=colors, data_map=data_map, grad_map=grad_map, formula_map=formula_map).source
            )
            info_ph.markdown(f'<div class="info-strip">Step {idx+1}: <b>{node.label or "node"}</b> — {step["formula"]}</div>', unsafe_allow_html=True)
            time.sleep(speed_b)

        info_ph.markdown('<div class="info-strip info-done">✅ Backprop complete! Every node now has its gradient.</div>', unsafe_allow_html=True)
    else:
        data_map = {id(n): n.data for n in topo}
        grad_map = {id(n): 0.0 for n in topo}
        st.graphviz_chart(draw_graph(root, data_map=data_map, grad_map=grad_map).source)
        st.caption("Press play — gradients start at 0, output seeds with grad = 1.")

    st.markdown('<div class="legend"><span>🔵 grad = 0</span><span>🟠 Computing now</span><span>🟢 grad done</span><span>🔴 High grad</span></div>', unsafe_allow_html=True)