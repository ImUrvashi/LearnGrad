"""Train MLP — TensorFlow-Playground-style live training on your own engine."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import plotly.graph_objects as go
from graphviz import Digraph
from engine.value import Value
from engine.nn import MLP
from game.xp import load_progress, save_progress, add_xp, award_badge

st.set_page_config(page_title="Train MLP | Gradient Quest", page_icon="🧠", layout="wide")
from game.ui import setup_chrome
setup_chrome()
st.title("🧠 Train Your MLP")
st.caption("A TensorFlow-Playground-style trainer — running entirely on your own autograd engine.")


# ── Helpers ──
def linspace(a, b, n):
    if n <= 1:
        return [a]
    step = (b - a) / (n - 1)
    return [a + step * i for i in range(n)]


def draw_network(model, input_labels):
    """Draw the MLP: neurons as circles, weights as colored edges (blue +, orange −)."""
    dot = Digraph(graph_attr={
        'rankdir': 'LR', 'nodesep': '0.22', 'ranksep': '0.9', 'bgcolor': 'transparent',
    })
    prev = []
    for i, lbl in enumerate(input_labels):
        nid = f"in{i}"
        dot.node(nid, lbl, shape='circle', style='filled', fillcolor='#8ecae6',
                 fontsize='11', width='0.45', fixedsize='true')
        prev.append(nid)

    for li, layer in enumerate(model.layers):
        is_out = (li == len(model.layers) - 1)
        cur = []
        for ni, neuron in enumerate(layer.neurons):
            nid = f"L{li}n{ni}"
            dot.node(nid, '', shape='circle', style='filled',
                     fillcolor='#ffd166' if is_out else '#e8e8e8',
                     width='0.4', fixedsize='true')
            for pid, w in zip(prev, neuron.w):
                wv = w.data
                color = '#1f77b4' if wv >= 0 else '#ff7f0e'  # blue positive, orange negative
                pen = f"{min(5.0, 0.4 + abs(wv) * 1.4):.2f}"
                dot.edge(pid, nid, color=color, penwidth=pen)
            cur.append(nid)
        prev = cur
    return dot


def decision_fig(model, xs, ys, res=18):
    """Heatmap of model output over the 2D input space, with data points overlaid."""
    xs0 = [p[0] for p in xs]
    xs1 = [p[1] for p in xs]
    xmin, xmax = min(xs0) - 0.5, max(xs0) + 0.5
    ymin, ymax = min(xs1) - 0.5, max(xs1) + 0.5
    xr = linspace(xmin, xmax, res)
    yr = linspace(ymin, ymax, res)

    Z = []
    for yv in yr:
        row = []
        for xv in xr:
            out = model([Value(xv), Value(yv)])
            row.append(out.data if isinstance(out, Value) else out)
        Z.append(row)

    fig = go.Figure(data=go.Heatmap(z=Z, x=xr, y=yr, colorscale='RdBu', zmid=0,
                                    opacity=0.85, showscale=False))
    fig.add_trace(go.Scatter(
        x=xs0, y=xs1, mode='markers',
        marker=dict(size=15, color=ys, colorscale='RdBu', cmid=0,
                    line=dict(width=2, color='white')),
        showlegend=False))
    fig.update_layout(title="Decision surface", template="plotly_dark", height=340,
                      margin=dict(l=10, r=10, t=40, b=10))
    return fig


def loss_fig(losses):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=losses, mode='lines', name='Loss',
                             line=dict(color='#58cc02', width=3)))
    fig.update_layout(title="Training loss", xaxis_title="Epoch", yaxis_title="Loss",
                      template="plotly_dark", height=300, margin=dict(l=10, r=10, t=40, b=10))
    return fig


# ── Dataset selection ──
dataset_name = st.selectbox("Dataset", ["XOR", "Simple Linear"])

if dataset_name == "XOR":
    xs = [[0, 0], [0, 1], [1, 0], [1, 1]]
    ys = [-1, 1, 1, -1]
    st.caption("Classic non-linear problem — needs a hidden layer to solve.")
else:
    xs = [[1, 0], [2, 0], [3, 0], [4, 0]]
    ys = [2, 4, 6, 8]
    st.caption("💡 Regression. Try ReLU — tanh saturates at large targets.")

# ── Architecture builder (TensorFlow-Playground style) ──
st.markdown("#### 🏗️ Network architecture")
top = st.columns([1, 1, 1])
num_layers = top[0].slider("Hidden layers", 1, 4, 2)
activation = top[1].selectbox("Activation", ["tanh", "relu", "sigmoid"])
lr = top[2].number_input("Learning rate", 0.001, 1.0, 0.05, step=0.01, format="%.3f")

layer_cols = st.columns(num_layers)
neuron_counts = []
for i in range(num_layers):
    n = layer_cols[i].number_input(f"Layer {i+1} neurons", 1, 8, 4, key=f"layer_{i}")
    neuron_counts.append(int(n))

architecture = neuron_counts + [1]
epochs = st.slider("Epochs", 10, 400, 120)

# Architecture summary
arch_str = " → ".join([str(len(xs[0]))] + [str(n) for n in architecture])
_tmp = MLP(len(xs[0]), architecture, activation=activation)
param_count = len(_tmp.parameters())
st.markdown(
    f"<div style='padding:8px 14px;border-radius:10px;border:1px solid rgba(128,128,128,0.3);"
    f"background:rgba(88,204,2,0.08);display:inline-block;font-weight:600'>"
    f"🔗 {arch_str}  ·  {param_count} parameters</div>",
    unsafe_allow_html=True,
)

st.divider()

# ══════════════════════════════════════════════════════════════
# Training dashboard layout
#   Row 1: metric strip (Epoch · Loss · Best)
#   Row 2: network diagram (full width)
#   Row 3: loss curve  |  decision surface
#   Row 4: results table (after training)
# ══════════════════════════════════════════════════════════════
input_labels = ["x₀", "x₁"]

# Row 1 — metrics
m1, m2, m3 = st.columns(3)
epoch_metric = m1.empty()
loss_metric = m2.empty()
best_metric = m3.empty()
epoch_metric.metric("Epoch", f"0/{epochs}")
loss_metric.metric("Loss", "—")
best_metric.metric("Best loss", "—")

# Row 2 — network diagram
st.markdown("##### 🧠 Network")
net_ph = st.empty()
net_ph.graphviz_chart(draw_network(_tmp, input_labels).source)
st.caption("🔵 positive weight · 🟠 negative weight · thickness = magnitude")

# Row 3 — charts side by side
chart_l, chart_r = st.columns(2)
chart_l.markdown("##### 📉 Training loss")
loss_ph = chart_l.empty()
chart_r.markdown("##### 🗺️ Decision surface")
bound_ph = chart_r.empty()
loss_ph.plotly_chart(loss_fig([]), use_container_width=True, key="loss_init")
bound_ph.plotly_chart(decision_fig(_tmp, xs, ys), use_container_width=True, key="bound_init")

# Row 4 — results placeholder
results_ph = st.container()

if st.button("🚀 Train", type="primary", use_container_width=True):
    model = MLP(len(xs[0]), architecture, activation=activation)
    losses = []
    best = float("inf")
    net_every = max(1, epochs // 30)
    bound_every = max(1, epochs // 10)

    for epoch in range(epochs):
        ypred = [model(x) for x in xs]
        loss = sum((yp - yt) ** 2 for yp, yt in zip(ypred, ys))

        model.zero_grad()
        loss.backward()
        for p in model.parameters():
            p.data -= lr * p.grad

        losses.append(loss.data)
        best = min(best, loss.data)

        if epoch % net_every == 0 or epoch == epochs - 1:
            net_ph.graphviz_chart(draw_network(model, input_labels).source)
            loss_ph.plotly_chart(loss_fig(losses), use_container_width=True, key=f"loss_{epoch}")
            epoch_metric.metric("Epoch", f"{epoch + 1}/{epochs}")
            loss_metric.metric("Loss", f"{loss.data:.4f}")
            best_metric.metric("Best loss", f"{best:.4f}")
        if epoch % bound_every == 0 or epoch == epochs - 1:
            bound_ph.plotly_chart(decision_fig(model, xs, ys), use_container_width=True, key=f"bound_{epoch}")

    # ── Results ──
    with results_ph:
        st.divider()
        res_l, res_r = st.columns([1, 1])
        with res_l:
            st.markdown("##### 📋 Final predictions")
            rows = []
            for x, yt in zip(xs, ys):
                out = model(x)
                pred = out.data if isinstance(out, Value) else out
                ok = "✅" if abs(pred - yt) < 0.5 else "❌"
                rows.append({"Input": str(x), "Pred": f"{pred:.2f}", "Target": yt, "": ok})
            st.dataframe(rows, hide_index=True, use_container_width=True, height=180)
        with res_r:
            st.markdown("##### 🏁 Outcome")
            if losses[-1] < 1.0:
                st.success(f"🎉 Converged! Final loss = {losses[-1]:.4f}")
                progress = load_progress()
                already = "Neural Trainer" in progress["badges"]
                progress = add_xp(progress, 50)
                progress = award_badge(progress, "Neural Trainer")
                save_progress(progress)
                st.info("+50 XP" if already else "+50 XP | 🏅 Neural Trainer badge earned!")
            else:
                st.warning(f"Final loss = {losses[-1]:.4f}.")
                st.caption("Try more epochs, a different learning rate, or more neurons.")