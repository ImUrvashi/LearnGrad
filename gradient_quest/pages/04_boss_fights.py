"""Boss Fights — Battle concepts to learn deep learning."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from auth import require_auth, get_current_user
import plotly.graph_objects as go
from engine.value import Value
from engine.nn import MLP
from game.bosses import BOSSES, evaluate_boss_choice
from game.xp import load_progress, save_progress, add_xp, award_badge

st.set_page_config(page_title="Boss Fights | Gradient Quest", page_icon="🐉", layout="wide")
from game.ui import setup_chrome
setup_chrome()

# ── Require authentication ──
require_auth()
user = get_current_user()
user_email = user["email"]

st.title("🐉 Boss Fights")

progress = load_progress(user_email=user_email)

for boss in BOSSES:
    badge_earned = boss["badge"] in progress["badges"]
    icon = "✅" if badge_earned else "⚔️"

    with st.expander(f"{icon} {boss['name']}", expanded=not badge_earned):
        st.markdown(f"*{boss['description']}*")

        if badge_earned:
            st.success(f"✅ Defeated! Badge earned: 🏅 {boss['badge']}")
            st.markdown(f"**Why?** {boss['explanation']}")
        else:
            choice = st.radio(
                "Choose your weapon:",
                boss["choices"],
                key=f"boss_{boss['id']}",
            )

            if st.button("⚔️ Fight!", key=f"fight_{boss['id']}"):
                won, explanation, xp_earned = evaluate_boss_choice(boss["id"], choice)

                if won:
                    st.success(f"🎉 You defeated the {boss['name']}!")
                    st.balloons()
                    st.markdown(f"**{explanation}**")
                    st.info(f"+{xp_earned} XP | 🏅 {boss['badge']} badge earned!")

                    progress = add_xp(progress, xp_earned)
                    progress = award_badge(progress, boss["badge"])
                    save_progress(progress, user_email=user_email)
                else:
                    st.error(f"💀 The {boss['name']} overpowered you!")
                    st.markdown(f"**Hint:** {explanation}")
                    st.warning("Try a different approach!")

                # Visualize gradient flow for the boss
                st.subheader("Gradient Flow Analysis")
                if boss["mechanic"] == "activation_choice":
                    # Show gradient magnitudes across layers for each activation
                    activations = boss["choices"]
                    results = {}

                    for act in activations:
                        act_lower = act.lower()
                        model = MLP(2, [4, 4, 4, 1], activation=act_lower)
                        out = model([Value(1.0), Value(1.0)])
                        out.backward()

                        layer_grads = []
                        for layer in model.layers:
                            grads = [abs(p.grad) for p in layer.parameters()]
                            avg = sum(grads) / len(grads) if grads else 0
                            layer_grads.append(avg)
                        results[act] = layer_grads

                    fig = go.Figure()
                    for act, grads in results.items():
                        fig.add_trace(go.Bar(
                            name=act,
                            x=[f"Layer {i+1}" for i in range(len(grads))],
                            y=grads,
                        ))
                    fig.update_layout(
                        title="Average Gradient Magnitude per Layer",
                        barmode='group',
                        template="plotly_dark",
                        height=350,
                    )
                    st.plotly_chart(fig, width="stretch")

                elif boss["mechanic"] == "depth_experiment":
                    # Show how gradients grow with network depth
                    depths = [3, 5, 8, 12]
                    max_grads = []

                    for depth in depths:
                        layers = [4] * depth + [1]
                        model = MLP(2, layers, activation='tanh')
                        out = model([Value(1.0), Value(1.0)])
                        out.backward()

                        all_grads = [abs(p.grad) for p in model.parameters()]
                        max_grads.append(max(all_grads) if all_grads else 0)

                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=[f"{d} layers" for d in depths],
                        y=max_grads,
                        marker_color=['#a8e6cf', '#ff9a3c', '#ff6b6b', '#ff0000'],
                    ))
                    fig.update_layout(
                        title="Max Gradient Magnitude vs Network Depth",
                        xaxis_title="Network Depth",
                        yaxis_title="Max |gradient|",
                        template="plotly_dark",
                        height=350,
                    )
                    st.plotly_chart(fig, width="stretch")
                    st.caption("As depth increases, gradients can explode — gradient clipping prevents this.")