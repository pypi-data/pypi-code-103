"""A Python implementation of the EMuLSion framework.

(Epidemiologic MUlti-Level SImulatiONs).

Field functions for environment management.

"""

import numpy                  as np


def rounding_policy(number, proportion):
    """Return the integer value corresponding to rounding
    proportion*number.

    """
    return np.rint(number * proportion).astype(int)


def binomial_policy(number, proportion):
    """Return a random binomial sample based on the parameters."""
    return np.random.binomial(number, proportion)


def evaporate(values, rate=0.1):
    """In-place 'evaporation'. The 'values' field is reduced by the
    'rate' factor. Values close to zero are replaced by zeros.

    """
    values *= 1 - rate
    values[np.isclose(values, 0)] = 0.



def diffuse2d(z_orig, diffusion=0.5, wrapx=False, wrapy=False):
    """In-place diffusion. The diffusion consists of replacing a part
    ('diffusion' parameter) of each value of the z_orig field by a
    contribution of the neighboring values (very similar to the
    discrete laplacian, but with consideration to the number of
    surrounding neighbors).

    """
    padshape = ((1, 1), (1, 1)) + tuple([(0, 0)
                                         for _ in range(len(z_orig.shape)-2)])
    # compute the number of neighbors for each cell
    neighbors = np.ones(z_orig.shape[:2]) * 8.0
    # Do not forget that in the field, x represent columns and y
    # lines.
    if not wrapx:
        neighbors[:, 0] = 5
        neighbors[:, -1] = 5
    if not wrapy:
        neighbors[0, :] = 5
        neighbors[-1, :] = 5
    if not wrapx and not wrapy:
        neighbors[0, 0] = 3
        neighbors[0, -1] = 3
        neighbors[-1, 0] = 3
        neighbors[-1, -1] = 3

    neighbors = neighbors.reshape(neighbors.shape +
                                  tuple([1] * (len(z_orig.shape)-2)))
    # compute the contribution of each neighbor
    z_wrap = np.pad(z_orig/neighbors, padshape, mode='wrap')
    if not wrapx:
        z_wrap[:, 0] = 0
        z_wrap[:, -1] = 0
    if not wrapy:
        z_wrap[0, :] = 0
        z_wrap[-1, :] = 0
    contribution = (z_wrap[:-2, :-2] + z_wrap[:-2, 1:-1] + z_wrap[:-2, 2:] +
                    z_wrap[1:-1, :-2]                    + z_wrap[1:-1, 2:] +
                    z_wrap[2:, :-2]  + z_wrap[2:, 1:-1]  + z_wrap[2:, 2:])
    z_orig *= 1.0 - diffusion
    z_orig += diffusion * contribution



def diffuse2d_anisotropic(z_orig,
                          attraction,
                          diffusion=np.array([0.5]),
                          wrapx=False,
                          wrapy=False):
    """In-place anisotropic diffusion. The anisotropic diffusion
    consists of replacing a part ('diffusion' parameter) of each value
    of the z_orig field by a contribution of the neighboring values
    according to their attractivity, specified in a separate
    matrix.

    """
    padshape = ((1, 1), (1, 1)) + tuple([(0, 0)
                                         for _ in range(len(z_orig.shape)-2)])
    if len(z_orig.shape) > 2:
        attraction = attraction.reshape(attraction.shape +
                                        tuple([1] * (len(z_orig.shape)-2)))
        if not isinstance(diffusion, float):
            diffusion = diffusion.reshape(diffusion.shape +
                                          tuple([1] * (len(z_orig.shape)-2)))

    att = np.pad(attraction, padshape, mode='wrap')
    if not wrapx:
        att[:, 0] = 0
        att[:, -1] = 0
    if not wrapy:
        att[0, :] = 0
        att[-1, :] = 0

    neighbors_att = (att[:-2, :-2] + att[:-2, 1:-1] + att[:-2, 2:] +
                     att[1:-1, :-2]                 + att[1:-1, 2:] +
                     att[2:, :-2]  + att[2:, 1:-1]  + att[2:, 2:])

    # since neighbors_att is used to normalize the attactivity of
    # neighboring celles, ensure that it is not 0
    neighbors_att[neighbors_att == 0] = 1.

    available = np.pad(z_orig * diffusion / neighbors_att, padshape, mode='wrap')
    if not wrapx:
        available[:, 0] = 0
        available[:, -1] = 0
    if not wrapy:
        available[0, :] = 0
        available[-1, :] = 0

    migration = attraction * (available[:-2, :-2] + available[:-2, 1:-1] + available[:-2, 2:] +
                              available[1:-1, :-2]                       + available[1:-1, 2:] +
                              available[2:, :-2]  + available[2:, 1:-1]  + available[2:, 2:])

    z_orig *= 1.0 - 1.0*diffusion
    z_orig += migration


def diffuse2d_general(z_orig,
                      attraction,
                      diffusion=np.array([0.5]),
                      radius=1,
                      wrapx=False,
                      wrapy=False):
    """In-place anisotropic diffusion with arbitrary radius (based on
    the Moore distance), including the original cell as a possible
    destination. The anisotropic diffusion consists of replacing a
    part ('diffusion' parameter) of each value of the z_orig field by
    a contribution of the neighboring values according to their
    attractivity, specified in a separate matrix.

    """
    height, width = z_orig.shape[:2]
    padshape = ((radius, radius), (radius, radius)) + tuple([(0, 0)
                                         for _ in range(len(z_orig.shape)-2)])
    # if more than 2D, reshape attraction and diffusion if needed
    if len(z_orig.shape) > len(attraction.shape):
        attraction = attraction.reshape(attraction.shape +
                                        tuple([1] * (len(z_orig.shape)-len(attraction.shape))))
        if not isinstance(diffusion, float):
            diffusion = diffusion.reshape(diffusion.shape +
                                          tuple([1] * (len(z_orig.shape)-len(diffusion.shape))))

    # compute attraction "around" each cell (wrt wrapping)
    att = np.pad(attraction, padshape, mode='wrap')
    if not wrapx:
        att[:, 0:radius] = 0
        att[:, (width+radius):(width + 2*radius)] = 0
    if not wrapy:
        att[0:radius, :] = 0
        att[(height+radius):(height + 2*radius), :] = 0

    # compute total attraction in the neighborhood of each cell
    neighbors_att = np.zeros(z_orig.shape, dtype=float)
    for dy in range(2*radius + 1):
        for dx in range(2*radius + 1):
            neighbors_att += att[dy:(dy + height), dx:(dx + width)]

    # since neighbors_att is used to normalize the attactivity of
    # neighboring cells, ensure that it is not 0
    neighbors_att[neighbors_att == 0] = 1.

    # ratio available for migration (leaving its original cell)
    available = np.pad(z_orig * diffusion / neighbors_att, padshape, mode='wrap')
    if not wrapx:
        available[:, 0:radius] = 0
        available[:, (width+radius):(width + 2*radius)] = 0
    if not wrapy:
        available[0:radius, :] = 0
        available[(height+radius):(height + 2*radius), :] = 0

    # quantity which actually moves towards each cell
    migration = np.zeros(z_orig.shape, dtype=float)
    for dy in range(2*radius + 1):
        for dx in range(2*radius + 1):
            migration += available[dy:(dy + height), dx:(dx + width)]
    migration *= attraction

    z_orig *= 1.0 - 1.0*diffusion
    z_orig += migration


def diffuse2d_stochastic(z_orig,
                         attraction,
                         diffusion=np.array([0.5]),
                         radius=1,
                         wrapx=False,
                         wrapy=False,
                         policy=binomial_policy):
    """In-place anisotropic stochastic diffusion with arbitrary radius
    (based on the Moore distance), including the original cell as a
    possible destination. The anisotropic diffusion consists of
    replacing a part ('diffusion' parameter) of each value of the
    z_orig field by a contribution of the neighboring values according
    to their attractivity, specified in a separate matrix. This
    diffusion is stochastic, which especially means that only integer
    values are considered, using 1) a user-defined vectorized function
    (policy) to compute the amount of the population that is expected
    to migrate (default: rounding), and 2) a multinomial sampling
    based on the relative attractivity of neighbours to determine the
    amount of the population that migrates in each surrounding cell.

    """
    height, width = z_orig.shape[:2]
    padshape = ((radius, radius), (radius, radius)) +\
      tuple([(0, 0) for _ in range(len(z_orig.shape)-2)])
    # if more than 2D, reshape attraction and diffusion if needed
    if len(z_orig.shape) > len(attraction.shape):
        attraction = attraction.reshape(attraction.shape +
                                        tuple([1] * (len(z_orig.shape)-len(attraction.shape))))
        if not isinstance(diffusion, float):
            diffusion = diffusion.reshape(diffusion.shape +
                                          tuple([1] * (len(z_orig.shape)-len(diffusion.shape))))

    # compute attraction "around" each cell (wrt wrapping)
    att = np.pad(attraction, padshape, mode='wrap')
    if not wrapx:
        att[:, 0:radius] = 0
        att[:, (width+radius):(width + 2*radius)] = 0
    if not wrapy:
        att[0:radius, :] = 0
        att[(height+radius):(height + 2*radius), :] = 0

    # compute connectivity between cells (depending on wrapping)
    comm_neighbors = np.ones(att.shape, dtype=int)
    if not wrapx:
        comm_neighbors[:, 0:radius] = 0
        comm_neighbors[:, (width+radius):(width + 2*radius)] = 0
    if not wrapy:
        comm_neighbors[0:radius, :] = 0
        comm_neighbors[(height+radius):(height + 2*radius), :] = 0

    # compute the number of neighbors of each cell
    nb_neighbors = np.zeros(z_orig.shape, dtype=int)
    for dy in range(2*radius+1):
        for dx in range(2*radius+1):
            nb_neighbors += comm_neighbors[dy:dy+height,dx:dx+width]

    # compute the total attractivity of the neighbors of each cell
    neighbors_att = np.zeros(z_orig.shape, dtype=float)
    for dy in range(2*radius + 1):
        for dx in range(2*radius + 1):
            neighbors_att += att[dy:(dy + height), dx:(dx + width)]

    # number of individuals allowed to migrate
    leaving = policy(z_orig, diffusion)
    # decrease the number of individuals remaining in their cell
    z_orig -= leaving
    # initialize migration
    migration = np.zeros(att.shape, dtype=int)
    # sum of "remaining" probabilities (to compute conditional probabilities)
    sum_probas = np.ones(z_orig.shape, dtype=float)
    # iterate over neighbors
    for dy in range(2*radius+1):
        for dx in range(2*radius+1):
            # except the original cell
            if dx != radius or dy != radius:
                # the "basic" probability (isotropic situation)
                # depends on the number of neighbors and the capacity
                # to reach the neighbor
                raw_probas = comm_neighbors[dy:dy+height, dx:dx+width] * np.ones(leaving.shape, dtype=float) / nb_neighbors
                # identify cells where total attractivity is not zero: otherwise, keep "anisotropic" behavior
                non_isotropic = np.nonzero(neighbors_att)
                # compute attractivity of the target cell (when non isotropic)
                local_att = att[dy:dy+height, dx:dx+width]
                # normalize by total attractivity to get the "basic" probability
                raw_probas[non_isotropic] = local_att[non_isotropic] / neighbors_att[non_isotropic]
                # initialize the number of individuals moving from their original cell to this neighbor
                moving = np.zeros(leaving.shape, dtype=int)
                # identify cells where no move is possible anymore
                left_to_move = np.nonzero(sum_probas)
                # compute the number of moving individuals with a
                # binomial sampling USING A CONDITIONAL PROBABILITY
                moving[left_to_move]  = np.random.binomial(leaving[left_to_move],
                                                           raw_probas[left_to_move] / sum_probas[left_to_move])
                # just in case, because very very low sum_probas lead to huge negative values
                moving[moving < 0] = 0
                # update migration
                migration[dy:dy+height, dx:dx+width] += moving
                # update sum of probas to compute conditional probabilities correctly
                sum_probas -= raw_probas
                # update the remaining individuals on cells
                leaving -= moving
    # update migration with individuals which stayed in their cell
    # print(migration.shape, leaving.shape)
    migration[radius:height+radius, radius:width+radius] += leaving
    # if wrapping environment, "fold" the pads back to the central area
    if wrapx:
        migration[radius:height+radius, width:width+radius] += migration[radius:height+radius, 0:radius]
        migration[radius:height+radius, radius:2*radius] += migration[radius:height+radius, width+radius:(width + 2*radius)]
    if wrapy:
        migration[height:height+radius, radius:width+radius] += migration[0:radius, radius:width+radius]
        migration[radius:2*radius, radius:width+radius] += migration[height+radius:(height + 2*radius), radius:width+radius]
    if wrapx and wrapy:
        migration[height:height+radius, width:width+radius] += migration[0:radius, 0:radius]
        migration[height:height+radius, radius:2*radius] += migration[0:radius, width+radius:(width + 2*radius)]
        migration[radius:2*radius, width:width+radius] += migration[height+radius:(height + 2*radius), 0:radius]
        migration[radius:2*radius, radius:2*radius] += migration[height+radius:(height + 2*radius),
                                                                 width+radius:(width + 2*radius)]
    # update final grid with the migration
    z_orig += migration[radius:height+radius, radius:width+radius]




def relative_coord_neighb(radius):
    return [(0,0)] + [(dy, dx) for dx in range(-radius, radius+1)
                      for dy in range(-radius, radius+1) if (dx, dy) != (0,0)]

def sum_neighbors_grid(values, radius, coord_neighb):
    """Return a grid width x height containing the number of neighbors of
       each cell, including itself.
    """
    height, width = values.shape[:2]
    padshape = ((radius, radius), (radius, radius))
    sum_values = np.copy(values) # beware, make a copy to avoid modification of 'values'
    nb = np.pad(sum_values, padshape, mode='constant')
    for (dy, dx) in coord_neighb:
        if not (dx == dy == 0):
            sum_values += nb[dy+radius:height+dy+radius,dx+radius:width+dx+radius]
    return sum_values

def nb_neighbors_grid(radius, width, height):
    """Return a grid width x height containing the number of neighbors of
       each cell, including itself.
    """
    return sum_neighbors_grid(np.ones((height, width), dtype=int), radius, relative_coord_neighb(radius)[1:])

def compute_neighborhood_3Dgrid(values, radius, neighborhood, coord_neighb):
    """Return a grid width x height x (2*radius+1)^2 containing the values of neighbors of
       each cell, including itself, dispatched in the 3rd dimension
    """
    height, width = values.shape[:2]
    result = np.zeros(values.shape[:2]+((2*radius+1)**2,))
    padshape = ((radius, radius), (radius, radius)) 
    #+ tuple([(0, 0) for _ in range(len(values.shape)-2)])
    val = np.pad(values, padshape, mode='constant')
    for (z, (dy, dx)) in enumerate(coord_neighb):
            result[...,z] = val[dy+radius:height+dy+radius,dx+radius:width+dx+radius] *\
                neighborhood[dy+radius:height+dy+radius,dx+radius:width+dx+radius]
            #print(z, dy, dx, result[...,z])
    return result


def reduce_neighborhood_3Dgrid(values, radius, coord_neighb, dtype=int):
    """Return a 2D grid by dispatching the 3rd dimension in the neighbor cells
    """
    height, width = values.shape[:2]
    padshape = ((radius, radius), (radius, radius))
    result = np.pad(np.zeros(values.shape[:-1], dtype=dtype), padshape, mode='constant')
    for (z, (dy, dx)) in enumerate(coord_neighb):
        result[dy+radius:height+dy+radius,dx+radius:width+dx+radius] += values[..., z]
    return result[radius:height+radius, radius:width+radius]

def diffuse_stoch2D(population,
                    attraction,
                    neighborhood,
                    coord_neigbhors,
                    diffusion=np.array([0.5]),
                    radius=1,
                    policy=binomial_policy):
    """In-place anisotropic stochastic diffusion with arbitrary radius
    (based on the Moore distance), including the original cell as a
    possible destination. The anisotropic diffusion consists of
    replacing a part ('diffusion' parameter) of each value of the
    population field by a contribution of the neighboring values according
    to their attractivity, specified in a separate matrix. This
    diffusion is stochastic, which especially means that only integer
    values are considered, using 1) a user-defined vectorized function
    (policy) to compute the amount of the population that is expected
    to migrate (default: rounding), and 2) a multinomial sampling
    based on the relative attractivity of neighbours to determine the
    amount of the population that migrates in each surrounding cell.

    Assumptions:
    - the topology of the grid (accessibility relations) is given through
      the neighborhood grid (2D grid + radius pad)
    - no cell with sum of neighbors attractivity = 0 and non-zero population

    """
    height, width = population.shape[:2]
    # compute attractivity of the neighbors as a 3rd dimension
    attr3d = compute_neighborhood_3Dgrid(attraction, 
                                         radius, 
                                         neighborhood, 
                                         relative_coord_neighb(radius))
    # compute total attractivity of the neighbors in each cell
    total_attr = np.sum(attr3d, axis=2)
    # compute probabilities for moving to neighbor cells
    probabilities = np.zeros(attr3d.shape)
    indices = np.nonzero(total_attr)
    probabilities[indices] = attr3d[indices] / np.reshape(total_attr, total_attr.shape+(1,))[indices]
    # number of individuals allowed to migrate
    leaving = policy(population, diffusion)
    population -= leaving
    # compute number of individuals moving from each cell to the neighbors
    coords = zip(*np.nonzero(leaving))
    movements = np.zeros(probabilities.shape, dtype=int)
    for coord in coords:
        movements[coord] = np.random.multinomial(leaving[coord], probabilities[coord])
    # aggregate 3rd dimension to dispatch moving individuals to the proper cells
    migration = reduce_neighborhood_3Dgrid(movements, radius, relative_coord_neighb(radius))
    population += migration



def multinomial_anyd(population, probas):
    """Compute a multinomial sampling over a multi-dimensional population, according
    to the probabilities. The population can be of any number N of dimensions.
    The probabilities has N dimensions (possibly 1-length) + a last dimension to
    represent the probability values for each cell.

    For instance for 2D diffusion on a population structured in 2D-grid with an
    additional '3rd' dimension representing e.g. an age structure, probabilities
    will be based on 2D, thus :
    - population is a Height x Width x Stages array
    - probabilities is Height x Width x 1 x Depth array
    where Depth is the number of possible outcomes for the multinomial sampling.
    This means that each value population[i, j, k] will be dispatched to Depth
    possible outcomes, according to probabilities[i, j, 0] for all k values.

    The result has the same dimensions as population + Depth.
    """
    depth = probas.shape[-1]
    multin = np.zeros(population.shape + (depth,), dtype=int)
    Sum = np.ones(probas.shape[:-1])
    avail = np.zeros(population.shape, dtype=int) + population
    for d in range(depth - 1):
        pr = np.where(Sum <= 0,
                      np.zeros(probas.shape[:-1]),
                      probas[..., d]/Sum)
        pr[pr < 0] = 0
        pr[np.isclose(pr, 0)] = 0
        pr[pr > 1] = 1
        multin[..., d] = np.random.binomial(avail, pr)
        avail -= multin[...,d]
        Sum -= probas[..., d]
    multin[..., -1] = avail
    return multin



def approx_diff(population, # H x W x D
                attraction, # H x W
                diffusion=np.array([0.5]),
                radius=1,
                policy=binomial_policy,
               ):
    """Approximation based on continuous diffusion"""
    height, width, depth = population.shape
    # number of individuals allowed to migrate
    leaving = policy(population, diffusion)
    population -= leaving
    # approximate diffusion through continuous values
    migration = np.zeros(leaving.shape) + leaving
    diffuse2d_general(migration, attraction, diffusion=diffusion, radius=radius)
    # update population
    moves = np.trunc(migration).astype(int)
    population += moves
    migration -= moves
    population += np.random.binomial(1, migration)



# diffusion in 3d
def diffuse_stoch_anyD(population, # H x W x D
                       attraction, # H x W
                       neighborhood, # pre-computed neighborhood relations
                       coord_neighbors, # pre-computed relative coordinates of neighbors
                       diffusion=np.array([0.5]),
                       radius=1,
                       policy=binomial_policy,
                       multin_func = multinomial_anyd):
    """In-place anisotropic stochastic diffusion with arbitrary radius
    (based on the Moore distance), including the original cell as a
    possible destination. The anisotropic diffusion consists of
    replacing a part ('diffusion' parameter) of each value of the
    population field by a contribution of the neighboring values according
    to their attractivity, specified in a separate matrix. This
    diffusion is stochastic, which especially means that only integer
    values are considered, using 1) a user-defined vectorized function
    (policy) to compute the amount of the population that is expected
    to migrate (default: rounding), and 2) a multinomial sampling
    based on the relative attractivity of neighbours to determine the
    amount of the population that migrates in each surrounding cell.

    Assumptions:
    - the topology of the grid (accessibility relations) is given through 
      the neighborhood grid (2D grid + radius pad)
    - no cell with sum of neighbors attractivity = 0 and non-zero population
       
    """
    height, width = population.shape[:2]
    # compute attractivity of the neighbors as a 3rd dimension
    attr3d = compute_neighborhood_3Dgrid(attraction, 
                                         radius,
                                         neighborhood, 
                                         coord_neighbors)
    # compute total attractivity of the neighbors in each cell (2D : row, col)                   
    total_attr = np.sum(attr3d, axis=2)
    # compute probabilities for moving to neighbor cells (3D : row, col, neighb)
    probabilities = np.zeros(attr3d.shape, dtype='double')
    indices = np.nonzero(total_attr)
    # compute non-zero probabilities only when non-zero sum of attractivities 
    probabilities[indices] = attr3d[indices] / total_attr.reshape(total_attr.shape+(1,))[indices]
    # add "fake" 3rd dimension if needed to allow shape matching between population and probabilities
    probabilities = probabilities.reshape(probabilities.shape[:-1] +\
                      tuple([1] * (len(population.shape) - len(probabilities.shape) + 1)) +\
                      (probabilities.shape[-1], ))
    # number of individuals allowed to migrate
    #leaving = np.zeros(population.shape, dtype='uint32') + policy(population, diffusion)
    leaving = policy(population, diffusion)
    population -= leaving
    # compute number of individuals moving from each cell to the neighbors
    movements = multin_func(leaving, probabilities)
    #movements = multin_3d(leaving, probabilities)
    # aggregate 3rd dimension to dispatch moving individuals to the proper cells
    migration = reduce_neighborhood_3Dgrid(movements, radius, coord_neighbors)
    population += migration
