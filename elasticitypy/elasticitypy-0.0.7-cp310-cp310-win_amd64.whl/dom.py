from typing import Callable, Dict, List, Tuple

from .mesh import Mesh, Group
from .expr import rust_func, Expr

from .elasticitypy import Nexus
from .seq import Seq


class Dom:
    pts: List[Tuple[float, float, float]]
    neg_dof: int
    ver_dof: Dict[int, Seq]
    edge_dof: Dict[Tuple[int, int], Seq]
    bc: List[float]
    nexus: Nexus

    def __init__(self, mesh: Mesh):
        self.pts = mesh.pts
        self.neg_dof, self.bc, self.sol = -1, [0.], []
        self.ver_dof = {ver: None for ver in range(len(mesh.pts))}
        self.edge_dof = {edge: None for edge in mesh.edges}
        self.nexus = Nexus(mesh.pts, mesh.tets)

    def plot_dom(self):
        return self.nexus.plot_dom()

    def embed_bc(self, func: Callable[[float, float, float], List[float]], group: Group):
        assert len(func(0., 0., 0.)) == 3
        neg_dof = self.neg_dof
        for ver in group.vers:
            if self.ver_dof[ver] is None:
                self.ver_dof[ver] = Seq(neg_dof, 3)
                neg_dof -= 3
                x, y, z = self.pts[ver]
                for val in func(x, y, z):
                    self.bc.append(val)
        for edge in group.edges:
            if self.edge_dof[edge] is None:
                self.edge_dof[edge] = Seq(neg_dof, 3)
                neg_dof -= 3
                x_i, y_i, z_i = self.pts[edge[0]]
                x_j, y_j, z_j = self.pts[edge[1]]
                x, y, z = 0.5 * (x_i + x_j), 0.5 * (y_i + y_j), 0.5 * (z_i + z_j)
                u = func(x, y, z)
                for val in u:
                    self.bc.append(val)
        self.neg_dof = neg_dof

    def set_cmat(self, cmat: List[List[float]]):
        self.nexus.set_cmat(cmat)

    def set_f(self, func: Callable[[float, float, float], List[float]], group: Group = None):
        assert len(func(0., 0., 0.)) == 3
        arena, [x, y, z] = rust_func(3)
        vec = func(x, y, z)
        csts = set()
        for expr in vec:
            if type(expr) is float:
                csts.add(expr)
        csts = {cst: arena.new_cst(cst) for cst in csts}
        vec = [expr.idx if type(expr) is Expr else csts[expr] for expr in vec]
        if group is None:
            self.nexus.set_f(0, set(), arena, vec)
        else:
            self.nexus.set_f(group.id, group.tets, arena, vec)

    def solve(self, tol: float = 1e-10):
        pos_dof = 0
        for ver in self.ver_dof:
            if self.ver_dof[ver] is None:
                self.ver_dof[ver] = Seq(pos_dof, 3)
                pos_dof += 3
        for edge in self.edge_dof:
            if self.edge_dof[edge] is None:
                self.edge_dof[edge] = Seq(pos_dof, 3)
                pos_dof += 3
        self.nexus.set_dof(self.ver_dof, self.edge_dof)
        self.nexus.set_solver(pos_dof, self.bc)
        self.nexus.assemble()
        self.nexus.solve(tol)

    def plot_disp(self):
        return self.nexus.plot_disp()

    def error(self, func: Callable[[float, float, float], List[float]]):
        assert len(func(0., 0., 0.)) == 3
        arena, [x, y, z] = rust_func(3)
        vec = func(x, y, z)
        csts = set()
        for expr in vec:
            if type(expr) is float:
                csts.add(expr)
        csts = {cst: arena.new_cst(cst) for cst in csts}
        vec = [expr.idx if type(expr) is Expr else csts[expr] for expr in vec]
        return self.nexus.error(arena, vec)
