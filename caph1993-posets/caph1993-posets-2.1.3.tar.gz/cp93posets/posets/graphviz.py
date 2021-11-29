from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .posets import Poset
from typing import Sequence, Tuple


def graphviz(
    n: int,
    edges: Sequence[Tuple[int, int]],
    labels: Sequence[str],
    blue_edges: Sequence[Tuple[int, int]] = None,
    save: str = None,
):
    'Show graph using graphviz. blue edges are extra edges'
    from pydotplus import graph_from_edges
    from pydotplus.graphviz import Node, Edge

    color = '#555555' if blue_edges is None else '#aaaaaa'

    g = graph_from_edges([], directed=True)
    g.set_rankdir('BT')  # type:ignore
    for i in range(n):
        style = {}
        g.add_node(Node(i, label=f'"{labels[i]}"', **style))
    for i, j in edges:
        style = {'dir': 'none', 'color': color}
        g.add_edge(Edge(i, j, **style))
    if blue_edges is not None:
        for i, j in blue_edges:
            style = {'color': 'blue', 'constraint': 'false'}
            g.add_edge(Edge(i, j, **style))

    png = g.create_png()  # type:ignore

    if save is None:
        import builtins
        if hasattr(builtins, '__IPYTHON__'):
            from IPython.display import display
            from IPython.display import Image
            img = Image(png)
            display(img)
        else:
            from io import BytesIO
            from PIL import Image
            img = Image.open(BytesIO(png))
            img.show()
    else:
        with open(save, 'wb') as f:
            f.write(png)
    return


def show(
    self: Poset,
    f=None,
    method='auto',
    labels=None,
    save=None,
):
    '''
    Use graphviz to display or save self as a Hasse diagram.
    The argument "method" (string) only affects visualization
    of the endomorphism f (if given). It can be
        - arrows: blue arrow from each node i to f[i]
        - labels: replace the label i of each node with f[i]
        - labels_bottom: (no label at i if f[i]=bottom)
        - arrows_bottom: (no arrow at i if f[i]=bottom)
        - auto: 'arrows_bottom' if self is a lattice and f preserves lub. 'arrows' otherwise.
    Hidding bottom is only allowed if self.bottom makes sense.
    '''
    methods = ('auto', 'labels', 'arrows', 'labels_bottom', 'arrows_bottom')
    assert method in methods, f'Unknown method "{method}"'

    if method == 'auto' and f is not None:
        if self.is_lattice and self.f_is_lub(f):
            method = 'arrows_bottom'
        else:
            method = 'arrows'
    n = self.n
    child = self.child
    blue_edges = None
    if labels is None:
        labels = self.labels
    if f is not None:
        enabled = not method.endswith('_bottom')
        ok = lambda fi: enabled or fi != self.bottom
        if method.startswith('arrows'):
            blue_edges = [(i, int(f[i])) for i in range(n) if ok(f[i])]
        else:
            gr = [[] for _ in range(n)]
            for i in range(n):
                if ok(f[i]):
                    gr[f[i]].append(i)
            labels = [','.join(map(str, l)) for l in gr]

    edges = [(i, j) for i in range(n) for j in range(n) if child[i, j]]
    graphviz(n, edges, labels=labels, blue_edges=blue_edges, save=save)
    return
