import numpy as np
from actomyosin_analyser.analysis.geometry import \
    (get_bounding_box,
     bounding_boxes_might_be_in_proximity)

def test_get_bounding_box():
    coords = np.array([[0., 5., 5.],
                       [5., 5., 5.],
                       [10., 5., 5.],
                       [5., 1., 5.],
                       [5., 20., 5.],
                       [5., 5., 2.],
                       [5., 5., 30.]])
    bb = get_bounding_box(coords)
    assert bb[0][0] == 0.
    assert bb[0][1] == 10.
    assert bb[1][0] == 1.0
    assert bb[1][1] == 20.0
    assert bb[2][0] == 2.0
    assert bb[2][1] == 30.0


def test_bounding_boxes_might_be_in_proximity():
    bb0 = np.array([[5., 15.], [15., 25.], [25., 35.]])
    bb1 = np.array([[14., 24.], [24., 34.], [34., 44.]]) # overlapping
    bb2 = np.array([[29., 34.], [24., 28.], [34., 38.]]) # x-distance
    bb3 = np.array([[95., 99.], [24., 28.], [34., 38.]]) # min-img-x-distance
    bb4 = np.array([[95., 99.], [90., 94.], [34., 38.]]) # min-img-xy-distance
    bb5 = np.array([[95., 99.], [90., 94.], [39., 124.]]) # min-img-xy-distance
                                                          # and both z close min-img-distance

    bb_other = np.empty((5, 3, 2))
    bb_other[0] = bb1
    bb_other[1] = bb2
    bb_other[2] = bb3
    bb_other[3] = bb4
    bb_other[4] = bb5
        
    min_img_box = np.array([100., 100., 100.])

    proximity = 0.0 # == direct overlap -> should yield only bb1
    candidates = bounding_boxes_might_be_in_proximity(proximity, bb0, bb_other, min_img_box) 

    assert candidates[0]
    assert not candidates[1]
    assert not candidates[2]
    assert not candidates[3]
    assert not candidates[4]

    proximity = 7.0 # should include bb1, bb3
    candidates = bounding_boxes_might_be_in_proximity(proximity, bb0, bb_other, min_img_box)

    assert candidates[0]
    assert not candidates[1]
    assert candidates[2]
    assert not candidates[3]
    assert not candidates[4]
    
    proximity = 15.0 # should include bb1, bb3, bb2

    candidates = candidates = bounding_boxes_might_be_in_proximity(proximity, bb0, bb_other, min_img_box)
    assert candidates[0]
    assert candidates[1]
    assert candidates[2]
    assert not candidates[3]
    assert not candidates[4]

    proximity = 21.85 # should exclude only bb4
    candidates = bounding_boxes_might_be_in_proximity(proximity, bb0, bb_other, min_img_box)

    assert candidates[0]
    assert candidates[1]
    assert candidates[2]
    assert candidates[3]
    assert candidates[4]
