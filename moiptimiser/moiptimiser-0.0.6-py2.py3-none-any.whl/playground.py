from moiptimiser.ozlen_2014_moiptimiser import Ozlen2014MOIPtimiser
optimiser = Ozlen2014MOIPtimiser.from_lp_file('../tests/examples/ozlen_2014_paper.as.max.lp')
nds = optimiser.find_non_dominated_objective_vectors()



{(-19, -15, -14, -11),      {(-19, -15, -14, -11),
 (-18, -15, -15, -9),        (-18, -15, -15, -9),
 (-17, -16, -13, -11),       (-17, -16, -13, -11),
 (-17, -13, -15, -11),       (-17, -13, -15, -11),
 (-16, -18, -15, -9),
 (-16, -15, -10, -13),       (-16, -15, -10, -13),
 (-15, -17, -11, -10),       (-15, -17, -11, -10),
 (-15, -16, -7, -12),        (-15, -16, -7, -12),
 (-14, -11, -16, -9),        (-14, -11, -16, -9),
 (-14, -8, -23, -13),        (-14, -8, -23, -13),
 (-13, -19, -17, -10),       (-13, -9, -16, -11),
 (-13, -9, -16, -11),
 (-12, -11, -11, -13),       (-12, -11, -11, -13)}
 (-11, -19, -12, -14)}



def print_vals(message, values):
    values = ['M' if value >= GRB.MAXINT
              else ('-M' if value <= -GRB.MAXINT else str(value))
              for value in values]
    print(f"{message}: [ {','.join(values)} ]")
