def get_topo_order(root):
    """Return topological order of the computation graph (inputs first)."""
    topo = []
    visited = set()

    def build(v):
        if v not in visited:
            visited.add(v)
            for child in v._prev:
                build(child)
            topo.append(v)

    build(root)
    return topo


def node_formula(node):
    """Return a human-readable numeric formula for how a node's value was computed.

    Examples: "2.00 * 3.00 = 6.00", "tanh(1.50) = 0.905", "3.00**2 = 9.00".
    Returns "" for input/leaf nodes (no operation).
    """
    if node._op and node._prev:
        children = list(node._prev)
        cvals = [f"{c.data:.2f}" for c in children]
        if node._op in ('+', '*') and len(cvals) >= 2:
            return f"{cvals[0]} {node._op} {cvals[1]} = {node.data:.2f}"
        elif node._op.startswith('**'):
            return f"{cvals[0]}{node._op} = {node.data:.2f}"
        else:
            return f"{node._op}({cvals[0]}) = {node.data:.3f}"
    return ""


def generate_forward_steps(root):
    """
    Generate step-by-step forward pass info.

    Returns list of dicts with node, label, op, value, step, desc, and formula.
    """
    topo = get_topo_order(root)
    steps = []
    for i, node in enumerate(topo):
        formula = node_formula(node)
        if formula:
            desc = formula
        else:
            desc = f"{node.label or 'input'} = {node.data:.2f}  (given input)"

        steps.append({
            "node": node,
            "label": node.label or f"node_{i}",
            "op": node._op,
            "value": node.data,
            "step": i + 1,
            "desc": desc,
            "formula": formula,
        })
    return steps