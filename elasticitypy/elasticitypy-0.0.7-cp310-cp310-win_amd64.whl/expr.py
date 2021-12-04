from .elasticitypy import Arena


class Expr:
    arena: Arena
    idx: int

    def __init__(self, idx: int, arena: Arena):
        self.idx = idx
        self.arena = arena

    def inv(self):
        idx = self.arena.inv(self.idx)
        return Expr(idx, self.arena)

    def sin(self):
        idx = self.arena.sin(self.idx)
        return Expr(idx, self.arena)

    def cos(self):
        idx = self.arena.cos(self.idx)
        return Expr(idx, self.arena)

    def exp(self):
        idx = self.arena.exp(self.idx)
        return Expr(idx, self.arena)

    def ln(self):
        idx = self.arena.ln(self.idx)
        return Expr(idx, self.arena)

    def __neg__(self):
        idx = self.arena.neg(self.idx)
        return Expr(idx, self.arena)

    def __add__(self, other):
        if type(other) == float:
            idx = self.arena.add_f64(self.idx, other)
            return Expr(idx, self.arena)
        elif type(other) == Expr:
            idx = self.arena.add(self.idx, other.idx)
            return Expr(idx, self.arena)

    def __sub__(self, other):
        if type(other) == float:
            idx = self.arena.sub_f64(self.idx, other)
            return Expr(idx, self.arena)
        elif type(other) == Expr:
            idx = self.arena.sub(self.idx, other.idx)
            return Expr(idx, self.arena)

    def __mul__(self, other):
        if type(other) == float:
            if other == 1.0:
                return self
            else:
                idx = self.arena.mul_f64(self.idx, other)
                return Expr(idx, self.arena)
        elif type(other) == Expr:
            idx = self.arena.mul(self.idx, other.idx)
            return Expr(idx, self.arena)

    def __div__(self, other):
        if type(other) == float:
            idx = self.arena.div_f64(self.idx, other)
            return Expr(idx, self.arena)
        elif type(other) == Expr:
            idx = self.arena.div(self.idx, other.idx)
            return Expr(idx, self.arena)

    def __radd__(self, other):
        if type(other) == float:
            idx = self.arena.rev_add_f64(other, self.idx)
            return Expr(idx, self.arena)

    def __rsub__(self, other):
        if type(other) == float:
            idx = self.arena.rev_sub_f64(other, self.idx)
            return Expr(idx, self.arena)

    def __rmul__(self, other):
        if type(other) == float:
            idx = self.arena.rev_mul_f64(other, self.idx)
            return Expr(idx, self.arena)

    def __rdiv__(self, other):
        if type(other) == float:
            idx = self.arena.rev_div_f64(other, self.idx)
            return Expr(idx, self.arena)

    def __pow__(self, other):
        assert type(other) == int
        idx = self.arena.pow(self.idx, float(other))
        return Expr(idx, self.arena)


def rust_func(num_args):
    arena = Arena()
    args = [Expr(arena.new_var(), arena) for _ in range(num_args)]
    return arena, args
