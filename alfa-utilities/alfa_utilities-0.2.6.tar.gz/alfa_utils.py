import numpy as np
import torch
import os
import json
import shutil


dataset_classnames = {
    'PASCAL VOC': ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog',
                   'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'],
    'KITTI': ['Car', 'Van', 'Pedestrian', 'Person_sitting', 'Cyclist'],
    'AI4ADAS': ['Car', 'Van', 'Pedestrian', 'Person_sitting', 'Cyclist', 'bus', 'car', 'truck', 'person', 'bicycle', 'van', 'pedestrian', 'person_sitting', 'cyclist'],

    'YOLO': ['Car', 'Van', 'Pedestrian', 'Person_sitting', 'Cyclist', 'bus', 'car', 'truck', 'person', 'bicycle', 'van', 'pedestrian', 'person_sitting', 'cyclist'],
    'YOLO CAR': ['Car', 'Van', 'bus', 'car', 'truck', 'van'],
    'YOLO PERSON': ['Pedestrian', 'Person_sitting', 'person', 'pedestrian', 'person_sitting'],
    'YOLO BICYCLE': ['Cyclist', 'bicycle', 'cyclist']
}


def box_corner_to_center(box):
    """Convert from (upper-left, lower-right) to (center, width, height)."""
    x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    w = x2 - x1
    h = y2 - y1
    box = torch.stack((cx, cy, w, h), axis=-1).numpy()
    return box


def box_center_to_corner(box):
    """Convert from (center, width, height) to (upper-left, lower-right)."""
    cx, cy, w, h = box[0], box[1], box[2], box[3]
    x1 = cx - 0.5 * w
    y1 = cy - 0.5 * h
    x2 = cx + 0.5 * w
    y2 = cy + 0.5 * h
    box = torch.stack((x1, y1, x2, y2), axis=-1).numpy()
    # box = torch.stack((x1, x2, y1, y2), axis=-1).numpy()
    return box


def to_alfa_labels(labels, alfa_labels):
    """Convert YOLO to ALFA class ids/labels."""
    for label in labels:
        to_alfa_label(label, alfa_labels)


def to_alfa_label(label, alfa_labels):
    """Convert YOLO to ALFA class ids/label."""
    if label in dataset_classnames['YOLO CAR']:  # YOLO car
        alfa_labels.append(dataset_classnames['PASCAL VOC'].index('car'))
    elif label in dataset_classnames['YOLO PERSON']:  # YOLO pedestrian
        alfa_labels.append(dataset_classnames['PASCAL VOC'].index(
            'person'))  # ALFA person
    elif label in dataset_classnames['YOLO BICYCLE']:  # YOLO cyclist
        alfa_labels.append(dataset_classnames['PASCAL VOC'].index(
            'bicycle'))  # ALFA bicycle


def to_ai4adas_label(label, ai4adas_labels):
    """Convert YOLO to AI4ADAS class ids/label."""
    if label in dataset_classnames['YOLO']:
        ai4adas_labels.append(label)


def convert_label_id_to_ai4adas_label(label_id):
    """Convert ALFA class id to YOLO label."""
    if label_id == dataset_classnames['PASCAL VOC'].index(
            'car'):
        return "car"  # YOLO Car
    elif label_id == dataset_classnames['PASCAL VOC'].index(
            'person'):
        return "pedestrian"  # YOLO Pedestrian
    elif label_id == dataset_classnames['PASCAL VOC'].index(
            'bicycle'):
        return "cyclist"  # YOLO Cyclist
    else:
        return "DontCare"


def calculate_class_scores_for_alfa(class_scores, detections, alfa_labels):
    """Transfer the class scores from YOLO dectections to ALFA list."""
    cls_scs = detections[:, 7].numpy()
    for i in range(len(cls_scs)):
        # There are 20 ALFA class ids, the first element in the class score is for the "no object" case.
        if alfa_labels[i] < len(dataset_classnames['PASCAL VOC']):
            class_scores[i, alfa_labels[i]+1] = cls_scs[i]


def prepare_for_alfa(detections, objects_pred, tail_img_name, for_alfa_detections, forJson=True, objects_labels=None, image_shape=(1, 1, 0)):
    """Save the ALFA related information."""
    alfa_bboxes, alfa_labels = [], []
    h, w, _ = image_shape
    if h == 0:
        h = 1
    if w == 0:
        w = 1

    # Get the predition 2d bounding boxes (left, top, bottom, right) for ALFA.
    for obj in objects_pred:
        if obj.type in ['DontCare']:
            continue
        alfa_bboxes.append(
            [obj.box2d[0]/w, obj.box2d[1]/h, obj.box2d[2]/w, obj.box2d[3]/h])

    # Get the labels for ALFA.
    pred_labels = []
    if len(objects_pred) > 0:
        for obj in objects_pred:
            pred_labels.append(obj.type)
    to_alfa_labels(pred_labels, alfa_labels)

    # Check, if label bounding boxes and ALFA bounding boxes match.
    if objects_labels is not None:
        for obj in objects_labels:
            if obj.cls_id != -1 and obj.type in dataset_classnames['YOLO']:
                ixmin, iymin, ixmax, iymax = obj.box2d[0], obj.box2d[1], obj.box2d[2], obj.box2d[3]
                for alfa_bbox in alfa_bboxes:
                    ixmin = np.maximum(ixmin, alfa_bbox[0])
                    iymin = np.maximum(iymin, alfa_bbox[1])
                    ixmax = np.minimum(ixmax, alfa_bbox[2])
                    iymax = np.minimum(iymax, alfa_bbox[3])
                if ixmax < ixmin or iymax < iymin:
                    print(
                        f'Caution: {tail_img_name} with {obj.type} results in ix/iy-max < ix/iy-min for bounding boxes (ALFA, labels)!')

    if alfa_labels:
        # According to the ALFA labels, there has to be 20 class ids of ALFA.
        # The additional first entry in the class scores vector is for the "no object" case.
        class_scores = np.zeros((len(alfa_labels), 21))
        calculate_class_scores_for_alfa(
            class_scores, detections, alfa_labels)
        if not pred_labels:
            class_scores[:, 0] = 1

        # Uncomment this, if you want to go the "pickle way".
        if forJson:
            class_scores = class_scores.tolist()

        for_alfa_detections.append(
            (tail_img_name, alfa_bboxes, alfa_labels, class_scores))


def first_lowercase(class_name):
    if not class_name:
        return
    else:
        return class_name[0].lower() + class_name[1:]


def detections_to_ai4adas_format(detections, objects_pred, ai4adas_objects, image_shape=(1, 1, 0)):
    """Save the AI4ADAS related information in a AI4ADAS specific format."""

    id = 0
    class_scores = detections[:, 7].numpy()
    h, w, _ = image_shape
    if h == 0:
        h = 1
    if w == 0:
        w = 1
    for obj in objects_pred:
        if obj.type in ['DontCare']:
            continue
        class_name = first_lowercase(str(obj.type))
        ai4adas_objects.append({"obj_id": str(id), "class_name": class_name,
                                "score": str(class_scores[id]), "xmin": str(obj.box2d[0]/w), "ymin": str(obj.box2d[1]/h), "xmax": str(obj.box2d[2]/w), "ymax": str(obj.box2d[3]/h)})
        id += 1
    # print(ai4adas_objects)


def to_ai4adas_format(bboxes, labels, class_scores, ai4adas_objects, image_shape=(1, 1, 0)):
    """Save the AI4ADAS related information (from YOLO) in a AI4ADAS specific format."""

    id = 0
    h, w, _ = image_shape
    if h == 0:
        h = 1
    if w == 0:
        w = 1
    for label in labels:
        class_name = first_lowercase(str(label))
        ai4adas_objects.append({"obj_id": str(id), "class_name": class_name,
                                "score": str(class_scores[id]), "xmin": str(bboxes[id][0]/w), "ymin": str(bboxes[id][1]/h), "xmax": str(bboxes[id][2]/w), "ymax": str(bboxes[id][3]/h)})
        id += 1
    # print(ai4adas_objects)


def convert_to_ai4adas_format(bboxes, label_ids, class_scores, ai4adas_objects, image_shape=(1, 1, 0)):
    """Convert the related information (from ALFA) in a AI4ADAS specific format."""

    id = 0
    h, w, _ = image_shape
    if h == 0:
        h = 1
    if w == 0:
        w = 1
    for label_id in label_ids:
        if label_id < len(dataset_classnames['PASCAL VOC']):
            ai4adas_objects.append({"obj_id": str(id), "class_name": convert_label_id_to_ai4adas_label(label_id),
                                    "score": str(class_scores[id][label_id+1]), "xmin": str(bboxes[id, 0]/w), "ymin": str(bboxes[id, 1]/h), "xmax": str(bboxes[id, 2]/w), "ymax": str(bboxes[id, 3]/h)})
        id += 1
    # print(ai4adas_alfa_full_detections)


def dictionaries_to_ai4adas_format(classes_dict, scores_dict, bboxes_dict, ai4adas_objects, image_shape=(1, 1, 0)):
    """Save dictionaries of bounding boxes et al. in AI4ADAS specific format.
    """

    h, w, _ = image_shape
    if h == 0:
        h = 1
    if w == 0:
        w = 1
    scores = scores_dict['ALFA']
    classes = classes_dict['ALFA']
    bboxes = bboxes_dict['ALFA']
    for i in range(classes.shape[0]):
        cls_id = int(classes[i])
        if cls_id >= 0:
            score = scores[i][1:][cls_id]
            ai4adas_objects.append({"obj_id": str(len(ai4adas_objects)), "class_name": str(dataset_classnames['PASCAL VOC'][classes[i]]),
                                    "score": str(score), "xmin": str(bboxes[i, 0]/w), "ymin": str(bboxes[i, 1]/h), "xmax": str(bboxes[i, 2]/w), "ymax": str(bboxes[i, 3]/h)})


def get_image_shape(detections, image_shapes):

    img_key = detections['img-name']
    if img_key not in image_shapes.keys():
        img_key = img_key.replace('.jpg', '.png')
        if img_key not in image_shapes.keys():
            img_key = img_key.replace('.png', '.jpg')

    if img_key in image_shapes:
        h, w, _ = image_shapes[img_key]
        if h == 0:
            h = 1
        if w == 0:
            w = 1
        return h, w
    else:
        return 1, 1


def from_ai4adas_to_alfa_format(ai4adas_alfa_detections, alfa_detections, image_shapes):
    """Convert information from the AI4ADAS into ALFA specific format."""

    for detections in ai4adas_alfa_detections:
        alfa_bboxes, alfa_labels, class_scores = [], [], []

        for det_objs in detections["objects"]:
            h, w = get_image_shape(detections, image_shapes)
            alfa_bboxes.append(
                [float(det_objs["xmin"])*w, float(det_objs["ymin"])*h, float(det_objs["xmax"])*w, float(det_objs["ymax"])*h])
            to_alfa_label(det_objs['class_name'], alfa_labels)
            class_scores.append(float(det_objs['score']))

        if alfa_labels:
            # According to the ALFA labels, there has to be 20 class ids of ALFA.
            # The additional first entry in the class scores vector is for the "no object" case.
            alfa_class_scores = np.zeros((len(alfa_labels), 21))
            for i in range(len(class_scores)):
                # There are 20 ALFA class ids, the first element in the class score is for the "no object" case.
                if alfa_labels[i] < len(dataset_classnames['PASCAL VOC']):
                    alfa_class_scores[i, alfa_labels[i]+1] = class_scores[i]
            alfa_class_scores = alfa_class_scores.tolist()

        alfa_detections.append(
            (detections["img-name"], alfa_bboxes, alfa_labels, alfa_class_scores if alfa_labels else class_scores))
        # print(alfa_detections)


def transfer_ai4adas_object_as_json(results_dir, image_file_name, alfa_path, ai4adas_object):
    """Save and transfer ALFA specific formatted object as json."""

    _, file_ext = os.path.splitext(image_file_name)
    image_file_json = image_file_name.replace(file_ext, '.json')
    with open(f"{results_dir}/{image_file_json}", 'w') as f:
        json.dump(ai4adas_object, f, ensure_ascii=False)

    if os.path.isdir(alfa_path):
        shutil.copy(
            f"{results_dir}/{image_file_json}", alfa_path)


def transfer_detections_to_alfa_path(results_dir, alfa_json_name, alfa_path, ai4adas_alfa_detections):
    """Save and transfer ALFA specific formatted object (with all detections)."""

    with open(f"{results_dir}/{alfa_json_name}.json", 'w') as f:
        json.dump(ai4adas_alfa_detections, f, ensure_ascii=False)

    if os.path.isdir(alfa_path):
        shutil.copy(
            f"{results_dir}/{alfa_json_name}.json", alfa_path)
