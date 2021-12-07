"""Implement kaibu-geojson-utils."""
import numpy as np
from geojson import Polygon as geojson_polygon
from geojson import Feature, FeatureCollection, dumps
from skimage import measure, morphology

from PIL import Image, ImageDraw
from skimage import draw as skimage_draw


def load_features(features, image_size):
    # Loop over list and create simple dictionary & get size of annotations
    annot_dict = {}
    roi_size_all = {}

    skipped = []

    if isinstance(features, dict) and "features" in features.keys():
        features = features["features"]
    for feat_idx, feat in enumerate(features):

        if feat["geometry"]["type"] not in ["Polygon", "LineString"]:
            skipped.append(feat["geometry"]["type"])
            continue

        # skip empty roi
        if len(feat["geometry"]["coordinates"][0]) <= 0:
            continue

        key_annot = "annot_" + str(feat_idx)
        annot_dict[key_annot] = {}
        annot_dict[key_annot]["type"] = feat["geometry"]["type"]
        annot_dict[key_annot]["pos"] = np.squeeze(
            np.asarray(feat["geometry"]["coordinates"])
        )
        annot_dict[key_annot]["properties"] = feat["properties"]

        # Store size of regions
        if not (feat["properties"]["label"] in roi_size_all):
            roi_size_all[feat["properties"]["label"]] = []

        roi_size_all[feat["properties"]["label"]].append(
            [
                annot_dict[key_annot]["pos"][:, 0].max()
                - annot_dict[key_annot]["pos"][:, 0].min(),
                annot_dict[key_annot]["pos"][:, 1].max()
                - annot_dict[key_annot]["pos"][:, 1].min(),
            ]
        )

    # print("Skipped geometry type(s):", skipped)
    return annot_dict, roi_size_all, image_size


def generate_binary_masks(
    annot_dict,
    image_size=(2048, 2048),
    erose_size=5,
    obj_size_rem=500,
    save_indiv=False,
):
    """
    Create masks from annotation dictionary

    Args:
        annot_dict (dictionary): dictionary with annotations

    Returns:
        mask_dict (dictionary): dictionary with masks
    """

    # Get dimensions of image and created masks of same size
    # This we need to save somewhere (e.g. as part of the geojson file?)

    # Filled masks and edge mask for polygons
    mask_fill = np.zeros(image_size, dtype=np.uint8)
    mask_edge = np.zeros(image_size, dtype=np.uint8)
    mask_labels = np.zeros(image_size, dtype=np.uint16)

    rr_all = []
    cc_all = []

    if save_indiv is True:
        mask_edge_indiv = np.zeros(
            (image_size[0], image_size[1], len(annot_dict)), dtype=np.bool
        )
        mask_fill_indiv = np.zeros(
            (image_size[0], image_size[1], len(annot_dict)), dtype=np.bool
        )

    # Image used to draw lines - for edge mask for freelines
    im_freeline = Image.new("1", (image_size[1], image_size[0]), color=0)
    draw = ImageDraw.Draw(im_freeline)

    # Loop over all roi
    i_roi = 0
    for roi_key, roi in annot_dict.items():
        roi_pos = roi["pos"]

        # Check region type

        # freeline - line
        if roi["type"] == "freeline" or roi["type"] == "LineString":

            # Loop over all pairs of points to draw the line

            for ind in range(roi_pos.shape[0] - 1):
                line_pos = (
                    roi_pos[ind, 1],
                    roi_pos[ind, 0],
                    roi_pos[ind + 1, 1],
                    roi_pos[ind + 1, 0],
                )
                draw.line(line_pos, fill=1, width=erose_size)

        # freehand - polygon
        elif (
            roi["type"] == "freehand"
            or roi["type"] == "polygon"
            or roi["type"] == "polyline"
            or roi["type"] == "Polygon"
        ):

            # Draw polygon
            rr, cc = skimage_draw.polygon(
                [image_size[0] - r for r in roi_pos[:, 1]], roi_pos[:, 0]
            )

            # Make sure it's not outside
            rr[rr < 0] = 0
            rr[rr > image_size[0] - 1] = image_size[0] - 1

            cc[cc < 0] = 0
            cc[cc > image_size[1] - 1] = image_size[1] - 1

            # Test if this region has already been added
            if any(np.array_equal(rr, rr_test) for rr_test in rr_all) and any(
                np.array_equal(cc, cc_test) for cc_test in cc_all
            ):
                # print('Region #{} has already been used'.format(i +
                # 1))
                continue

            rr_all.append(rr)
            cc_all.append(cc)

            # Generate mask
            mask_fill_roi = np.zeros(image_size, dtype=np.uint8)
            mask_fill_roi[rr, cc] = 1

            # Erode to get cell edge - both arrays are boolean to be used as
            # index arrays later
            mask_fill_roi_erode = morphology.binary_erosion(
                mask_fill_roi, np.ones((erose_size, erose_size))
            )
            mask_edge_roi = (
                mask_fill_roi.astype("int") - mask_fill_roi_erode.astype("int")
            ).astype("bool")

            # Save array for mask and edge
            mask_fill[mask_fill_roi > 0] = 1
            mask_edge[mask_edge_roi] = 1
            mask_labels[mask_fill_roi > 0] = i_roi + 1

            if save_indiv is True:
                mask_edge_indiv[:, :, i_roi] = mask_edge_roi.astype("bool")
                mask_fill_indiv[:, :, i_roi] = mask_fill_roi_erode.astype("bool")

            i_roi = i_roi + 1

        else:
            roi_type = roi["type"]
            raise NotImplementedError(
                f'Mask for roi type "{roi_type}" can not be created'
            )

    del draw

    # Convert mask from free-lines to numpy array
    mask_edge_freeline = np.asarray(im_freeline)
    mask_edge_freeline = mask_edge_freeline.astype("bool")

    # Post-processing of fill and edge mask - if defined
    mask_dict = {}
    if np.any(mask_fill):

        # (1) remove edges , (2) remove small  objects
        mask_fill = mask_fill & ~mask_edge
        mask_fill = morphology.remove_small_objects(
            mask_fill.astype("bool"), obj_size_rem
        )

        # For edge - consider also freeline edge mask

        mask_edge = mask_edge.astype("bool")
        mask_edge = np.logical_or(mask_edge, mask_edge_freeline)

        # Assign to dictionary for return
        mask_dict["edge"] = mask_edge
        mask_dict["fill"] = mask_fill.astype("bool")
        mask_dict["labels"] = mask_labels.astype("uint16")

        if save_indiv is True:
            mask_dict["edge_indiv"] = mask_edge_indiv
            mask_dict["fill_indiv"] = mask_fill_indiv
        else:
            mask_dict["edge_indiv"] = np.zeros(image_size + (1,), dtype=np.uint8)
            mask_dict["fill_indiv"] = np.zeros(image_size + (1,), dtype=np.uint8)

    # Only edge mask present
    elif np.any(mask_edge_freeline):
        mask_dict["edge"] = mask_edge_freeline
        mask_dict["fill"] = mask_fill.astype("bool")
        mask_dict["labels"] = mask_labels.astype("uint16")

        mask_dict["edge_indiv"] = np.zeros(image_size + (1,), dtype=np.uint8)
        mask_dict["fill_indiv"] = np.zeros(image_size + (1,), dtype=np.uint8)

    else:
        raise Exception("No mask has been created.")

    return mask_dict


def features_to_mask(
    features,
    image_size,
):
    # Read annotation:  Correct class has been selected based on annot_type
    annot_dict_all, roi_size_all, image_size = load_features(features, image_size)

    annot_types = set(
        annot_dict_all[k]["properties"]["label"] for k in annot_dict_all.keys()
    )
    mask_dict = None
    for annot_type in annot_types:
        # print("annot_type: ", annot_type)
        # Filter the annotations by label
        annot_dict = {
            k: annot_dict_all[k]
            for k in annot_dict_all.keys()
            if annot_dict_all[k]["properties"]["label"] == annot_type
        }
        # Create masks
        # Binary - is always necessary to creat other masks
        mask_dict = generate_binary_masks(
            annot_dict,
            image_size=image_size,
            erose_size=5,
            obj_size_rem=500,
            save_indiv=True,
        )
    return np.flipud(mask_dict["labels"])


def _convert_mask(img_mask, label=None):
    # for img_mask, for cells on border, should make sure on border pixels are # set to 0
    shape_x, shape_y = img_mask.shape
    shape_x, shape_y = shape_x - 1, shape_y - 1
    img_mask[0, :] = img_mask[:, 0] = img_mask[shape_x, :] = img_mask[:, shape_y] = 0
    features = []
    label = label or "cell"
    # Get all object ids, remove 0 since this is background
    ind_objs = np.unique(img_mask)
    ind_objs = np.delete(ind_objs, np.where(ind_objs == 0))
    for obj_int in np.nditer(ind_objs, flags=["zerosize_ok"]):
        # Create binary mask for current object and find contour
        img_mask_loop = np.zeros((img_mask.shape[0], img_mask.shape[1]))
        img_mask_loop[img_mask == obj_int] = 1
        contours_find = measure.find_contours(img_mask_loop, 0.5)
        if len(contours_find) == 1:
            index = 0
        else:
            pixels = []
            for _, item in enumerate(contours_find):
                pixels.append(len(item))
            index = np.argmax(pixels)
        contour = contours_find[index]

        contour_as_numpy = contour[:, np.argsort([1, 0])]
        contour_as_numpy[:, 1] = np.array([img_mask.shape[0] - h[0] for h in contour])
        contour_asList = contour_as_numpy.tolist()

        # Create and append feature for geojson
        pol_loop = geojson_polygon([contour_asList])

        full_label = label + "_idx"
        index_number = int(obj_int - 1)
        features.append(
            Feature(
                geometry=pol_loop, properties={full_label: index_number, "label": label}
            )
        )
    return features


def mask_to_geojson(img_mask, label=None):
    """
    Args:
      img_mask (numpy array): numpy data, with each object being assigned with a unique uint number
      label (str): like 'cell', 'nuclei'
    """
    features = _convert_mask(np.flipud(img_mask), label=label)
    feature_collection = FeatureCollection(
        features, bbox=[0, 0, img_mask.shape[1] - 1, img_mask.shape[0] - 1]
    )
    geojson_str = dumps(feature_collection, sort_keys=True)
    return geojson_str


def mask_to_features(img_mask, label=None):
    """
    Args:
      img_mask (numpy array): numpy data, with each object being assigned with a unique uint number
      label (str): like 'cell', 'nuclei'
    """
    features = _convert_mask(np.flipud(img_mask), label=label)
    features = list(
        map(
            lambda feature: np.array(
                feature["geometry"]["coordinates"][0], dtype="uint16"
            ).tolist(),
            features,
        )
    )
    return features
