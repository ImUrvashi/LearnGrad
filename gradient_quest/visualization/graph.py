from graphviz import Digraph


def trace(root):
    """Build sets of all nodes and edges in the computation graph."""
    nodes, edges = set(), set()

    def build(v):
        if v not in nodes:
            nodes.add(v)
            for child in v._prev:
                edges.add((child, v))
                build(child)

    build(root)
    return nodes, edges


def draw_graph(root, format='svg', rankdir='LR', node_colors=None,
               data_map=None, grad_map=None, formula_map=None):
    """
    Render a computation graph rooted at `root` as a Graphviz Digraph.

    Args:
        root: Value node at the root of the graph.
        format: Output format (svg, png, etc.).
        rankdir: Layout direction ('LR' = left-to-right, 'TB' = top-to-bottom).
        node_colors: Optional dict mapping Value id -> fillcolor string.
        data_map: Optional dict id -> displayed data value. If provided, nodes not
                  in the map show "?"; overrides the node's actual .data.
        grad_map: Optional dict id -> displayed grad value. Same behaviour as data_map.
        formula_map: Optional dict id -> formula string to display as an extra row
                     inside the node (e.g. "2.00 * 3.00 = 6.00").

    Returns:
        graphviz.Digraph object.
    """
    node_colors = node_colors or {}
    dot = Digraph(format=format, graph_attr={'rankdir': rankdir})

    nodes, _ = trace(root)

    for n in nodes:
        label = n.label or ''
        uid = str(id(n))
        fillcolor = node_colors.get(id(n), 'white')

        # Displayed data value
        if data_map is not None:
            dv = data_map.get(id(n))
            data_str = f"{dv:.3f}" if dv is not None else "?"
        else:
            data_str = f"{n.data:.3f}"

        # Displayed grad value
        if grad_map is not None:
            gv = grad_map.get(id(n))
            grad_str = f"{gv:.3f}" if gv is not None else "?"
        else:
            grad_str = f"{n.grad:.3f}"

        rows = []
        if label:
            rows.append(label)
        if formula_map and formula_map.get(id(n)):
            rows.append(formula_map[id(n)])
        rows.append(f"data {data_str}")
        rows.append(f"grad {grad_str}")
        node_label = "{ " + " | ".join(rows) + " }"

        dot.node(
            name=uid,
            label=node_label,
            shape='record',
            style='filled',
            fillcolor=fillcolor,
        )

        if n._op:
            op_uid = uid + n._op
            dot.node(name=op_uid, label=n._op, shape='circle', style='filled',
                     fillcolor='lightyellow')
            dot.edge(op_uid, uid)

            for child in n._prev:
                dot.edge(str(id(child)), op_uid)

    return dot