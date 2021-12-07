import numpy as np
import torch
import os
import json
import shutil

from pathlib import Path


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


class ALFA_Utils:

    def __init__(self, alfa_results_dir, alfa_path_detections, alfa_path_gt, save_alfa=True, save_gt=False):
        """
         ALFA Utilities class

        ----------
        alfa_results_dir : str
            internal directory to store the (fusion) results
        alfa_path_detections : str
            external directory to transfer the detections of the base detector (within one json file)
        alfa_path_gt : str
            external directory to transfer the detections of the base detector as ground truth (one json file per image)
        save_alfa: bool
            Save and transfer of the fusion results?
        save_gt: bool
            Save and transfer of the ground truth results?

        """
        self.alfa_results_dir = alfa_results_dir
        ALFA_Utils.create_dir(self.alfa_results_dir)
        self.alfa_path_detections = alfa_path_detections
        ALFA_Utils.create_dir(self.alfa_path_detections)
        self.alfa_path_ground_truth = alfa_path_gt
        ALFA_Utils.create_dir(self.alfa_path_ground_truth)

        self.save_alfa = save_alfa
        self.save_ground_truth = save_gt

    def transfer_ground_truth_to_alfa_path(self, image_file_name, ai4adas_object):
        """Save and transfer single ALFA specific formatted object as ground truth json."""

        if self.save_ground_truth:
            _, file_ext = os.path.splitext(image_file_name)
            image_file_json = image_file_name.replace(file_ext, '.json')
            results_file = os.path.join(self.alfa_results_dir, image_file_json)
            with open(results_file, 'w') as f:
                json.dump(ai4adas_object, f, ensure_ascii=False)

            if os.path.isdir(self.alfa_path_ground_truth):
                shutil.copy(results_file, self.alfa_path_ground_truth)

            print(
                f'\nWriting {image_file_json} for ALFA within {self.alfa_path_ground_truth} folder...')

            return image_file_json

    def transfer_detections_to_alfa_path(self, alfa_json_name, ai4adas_alfa_detections):
        """Save and transfer ALFA specific formatted object (with all detections)."""

        if self.save_alfa:
            results_file_name = os.path.join(
                self.alfa_results_dir, alfa_json_name)
            with open(f"{results_file_name}.json", 'w') as f:
                json.dump(ai4adas_alfa_detections, f, ensure_ascii=False)

            if os.path.isdir(self.alfa_path_detections):
                shutil.copy(f"{results_file_name}.json",
                            self.alfa_path_detections)

            print(
                f'\nWriting {alfa_json_name}.json for ALFA within {self.alfa_results_dir} folder...')

    def create_dir(dir_to_create):
        """Create storage directory."""

        if not os.path.isdir(dir_to_create):
            Path(dir_to_create).mkdir(parents=True, exist_ok=True)

            print(
                f'\nCreating ALFA directory {dir_to_create}...')

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
            ALFA_Utils.to_alfa_label(label, alfa_labels)

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

        if label in dataset_classnames['AI4ADAS']:
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
        h, w = ALFA_Utils.check_image_shape(image_shape)

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
        ALFA_Utils.to_alfa_labels(pred_labels, alfa_labels)

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
            ALFA_Utils.calculate_class_scores_for_alfa(
                class_scores, detections, alfa_labels)
            if not pred_labels:
                class_scores[:, 0] = 1

            # Uncomment this, if you want to go the "pickle way".
            if forJson:
                class_scores = class_scores.tolist()

            for_alfa_detections.append(
                (tail_img_name, alfa_bboxes, alfa_labels, class_scores))

    def first_lowercase(class_name):
        """Lower the first character of a string."""

        if not class_name:
            return
        else:
            return class_name[0].lower() + class_name[1:]

    def detections_to_ai4adas_format(detections, objects_pred, ai4adas_objects, image_shape=(1, 1, 0)):
        """Save the AI4ADAS related information in a AI4ADAS specific format."""

        id = 0
        class_scores = detections[:, 7].numpy()
        h, w = ALFA_Utils.check_image_shape(image_shape)

        for obj in objects_pred:
            if obj.type in ['DontCare']:
                continue
            class_name = ALFA_Utils.first_lowercase(str(obj.type))
            ai4adas_objects.append({"obj_id": str(id), "class_name": class_name,
                                    "score": str(class_scores[id]), "xmin": str(obj.box2d[0]/w), "ymin": str(obj.box2d[1]/h), "xmax": str(obj.box2d[2]/w), "ymax": str(obj.box2d[3]/h)})
            id += 1
        # print(ai4adas_objects)

    def to_ai4adas_format(bboxes, labels, class_scores, ai4adas_objects, image_shape=(1, 1, 0)):
        """Save the AI4ADAS related information (from YOLO) in a AI4ADAS specific format."""

        id = 0
        h, w = ALFA_Utils.check_image_shape(image_shape)

        for label in labels:
            class_name = ALFA_Utils.first_lowercase(str(label))
            ai4adas_objects.append({"obj_id": str(id), "class_name": class_name,
                                    "score": str(class_scores[id]), "xmin": str(bboxes[id][0]/w), "ymin": str(bboxes[id][1]/h), "xmax": str(bboxes[id][2]/w), "ymax": str(bboxes[id][3]/h)})
            id += 1
        # print(ai4adas_objects)

    def convert_to_ai4adas_format(bboxes, label_ids, class_scores, ai4adas_objects, image_shape=(1, 1, 0)):
        """Convert the related information (from ALFA) in a AI4ADAS specific format."""

        id = 0
        h, w = ALFA_Utils.check_image_shape(image_shape)

        for label_id in label_ids:
            if label_id < len(dataset_classnames['PASCAL VOC']):
                ai4adas_objects.append({"obj_id": str(id), "class_name": ALFA_Utils.convert_label_id_to_ai4adas_label(label_id),
                                        "score": str(class_scores[id][label_id+1]), "xmin": str(bboxes[id, 0]/w), "ymin": str(bboxes[id, 1]/h), "xmax": str(bboxes[id, 2]/w), "ymax": str(bboxes[id, 3]/h)})
            id += 1
        # print(ai4adas_alfa_full_detections)

    def dictionaries_to_ai4adas_format(classes_dict, scores_dict, bboxes_dict, ai4adas_objects, image_shape=(1, 1, 0)):
        """Save dictionaries of bounding boxes et al. in AI4ADAS specific format."""

        h, w = ALFA_Utils.check_image_shape(image_shape)
        scores = scores_dict['ALFA']
        classes = classes_dict['ALFA']
        bboxes = bboxes_dict['ALFA']

        for i in range(classes.shape[0]):
            cls_id = int(classes[i])
            if cls_id >= 0:
                score = scores[i][1:][cls_id]
                ai4adas_objects.append({"obj_id": str(len(ai4adas_objects)), "class_name": str(dataset_classnames['PASCAL VOC'][classes[i]]),
                                        "score": str(score), "xmin": str(bboxes[i, 0]/w), "ymin": str(bboxes[i, 1]/h), "xmax": str(bboxes[i, 2]/w), "ymax": str(bboxes[i, 3]/h)})

    def check_image_shape(image_shape):
        """Check for valid image shape."""

        if image_shape is None:
            return 1, 1

        h, w, _ = image_shape
        if h == 0:
            h = 1
        if w == 0:
            w = 1
        return h, w

    def get_image_shape(detections, image_shapes):
        """Get valid image shape for detection."""

        img_key = detections['img-name']
        if img_key not in image_shapes.keys():
            img_key = img_key.replace('.jpg', '.png')
            if img_key not in image_shapes.keys():
                img_key = img_key.replace('.png', '.jpg')

        if img_key in image_shapes:
            h, w = ALFA_Utils.check_image_shape(image_shapes[img_key])
            return h, w
        else:
            return 1, 1

    def from_ai4adas_to_alfa_format(ai4adas_alfa_detections, alfa_detections, image_shapes):
        """Convert information from the AI4ADAS into ALFA specific format."""

        for detections in ai4adas_alfa_detections:
            alfa_bboxes, alfa_labels, class_scores = [], [], []

            for det_objs in detections["objects"]:
                h, w = ALFA_Utils.get_image_shape(detections, image_shapes)
                alfa_bboxes.append(
                    [float(det_objs["xmin"])*w, float(det_objs["ymin"])*h, float(det_objs["xmax"])*w, float(det_objs["ymax"])*h])
                ALFA_Utils.to_alfa_label(det_objs['class_name'], alfa_labels)
                class_scores.append(float(det_objs['score']))

            if alfa_labels:
                # According to the ALFA labels, there has to be 20 class ids of ALFA.
                # The additional first entry in the class scores vector is for the "no object" case.
                alfa_class_scores = np.zeros((len(alfa_labels), 21))
                for i in range(len(class_scores)):
                    # There are 20 ALFA class ids, the first element in the class score is for the "no object" case.
                    if alfa_labels[i] < len(dataset_classnames['PASCAL VOC']):
                        alfa_class_scores[i,
                                          alfa_labels[i]+1] = class_scores[i]
                alfa_class_scores = alfa_class_scores.tolist()

            alfa_detections.append(
                (detections["img-name"], alfa_bboxes, alfa_labels, alfa_class_scores if alfa_labels else class_scores))
            # print(alfa_detections)
