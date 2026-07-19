from .forward_pass import get_topo_order
from .graph import trace


# Color scheme for backprop visualization
COLORS = {
    "unvisited": "#a8d8ea",   # blue
    "active": "#ff9a3c",      # orange
    "computed": "#a8e6cf",    # green
    "high_grad": "#ff6b6b",   # red
}


def _build_consumers(root):
    """Map each node id -> list of parent (consumer) nodes that use it."""
    consumers = {}
    nodes, _ = trace(root)
    for n in nodes:
        for child in n._prev:
            consumers.setdefault(id(child), []).append(n)
    return consumers


def _local_derivative(parent, node):
    """Return the local derivative of `parent` output w.r.t. its input `node`."""
    op = parent._op
    if op == '+':
        return 1.0
    if op == '*':
        others = [c for c in parent._prev if c is not node]
        return others[0].data if others else 1.0
    if op.startswith('**'):
        try:
            k = float(op[2:])
        except ValueError:
            return 1.0
        return k * (node.data ** (k - 1))
    if op == 'tanh':
        return 1 - parent.data ** 2
    if op == 'relu':
        return 1.0 if parent.data > 0 else 0.0
    if op == 'sigmoid':
        return parent.data * (1 - parent.data)
    if op == 'exp':
        return parent.data
    return 1.0


def _grad_explanation(node, consumers, is_root):
    """Build a chain-rule explanation string for a node's gradient."""
    if is_root:
        return "seed: grad = 1  (output)"
    parts = []
    for p in consumers.get(id(node), []):
        deriv = _local_derivative(p, node)
        parts.append(f"{deriv:.2f}*{p.grad:.2f}")
    if parts:
        return " + ".join(parts) + f" = {node.grad:.2f}"
    return f"grad = {node.grad:.2f}"


def generate_backprop_steps(root):
    """
    Generate step-by-step backprop info.

    Runs backward() first, then returns a list of steps (output-first order) showing
    the gradient propagation, each with a chain-rule explanation.
    """
    # Run backward to compute all gradients
    root.backward()

    reverse_topo = list(reversed(get_topo_order(root)))
    consumers = _build_consumers(root)
    steps = []

    for i, node in enumerate(reverse_topo):
        is_root = (node is root)
        explanation = _grad_explanation(node, consumers, is_root)
        desc = f"{node.label or 'node'}: {explanation}"

        steps.append({
            "node": node,
            "label": node.label or f"node_{i}",
            "grad": node.grad,
            "op": node._op,
            "step": i + 1,
            "desc": desc,
            "formula": explanation,
        })

    return steps


def get_node_colors_at_step(steps, current_step):
    """
    Return a dict mapping Value id -> color for rendering at a given step.

    - Steps before current_step: green (computed)
    - Step at current_step: orange (active)
    - Steps after current_step: blue (unvisited)
    - Any node with |grad| > 2.0 at computed steps: red (high gradient)
    """
    colors = {}
    for s in steps:
        node_id = id(s["node"])
        if s["step"] < current_step:
            if abs(s["grad"]) > 2.0:
                colors[node_id] = COLORS["high_grad"]
            else:
                colors[node_id] = COLORS["computed"]
        elif s["step"] == current_step:
            colors[node_id] = COLORS["active"]
        else:
            colors[node_id] = COLORS["unvisited"]
    return colors