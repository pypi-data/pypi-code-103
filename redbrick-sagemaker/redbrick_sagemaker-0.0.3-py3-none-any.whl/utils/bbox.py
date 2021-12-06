"""Utility functions for bounding box jobs."""
import os
import json

from typing import Dict, Tuple

import numpy as np
import tqdm
import imageio

from redbrick_sagemaker.utils.redbrick import create_taxonomy_map
from .im2rec import run_im2rec


def convert_sagemaker_rbai_bbox(  # pylint: disable=too-many-locals
    prediction_dir: str,
    tasks: Dict,
    taxonomy: Dict[int, str],
    thresh: float = 0.4,
):
    """
    Convert a sagemaker detection to rbai task.

    Parameters
    ------------
    prediction_dir: str
        Local path where the prediction files are stored.
        The filenames will be task_id.png.out

    tasks: List[Dict]
        RBAI task objects for which the predictions are stored
        in prediction_dir

    taxonomy: Dict[int, str]
        maps from class_id to class_name

    thresh: float = 0.4
        confidence below this threshold will be ignored.

    Returns
    ------------
    labeled_tasks: List[Dict]
        Returns all the tasks with labels.
    """
    labeled_tasks = []
    for task in tasks:
        task_id = task["taskId"]
        prediction_file = os.path.join(prediction_dir, f"{task_id}.png.out")

        # read single pred file
        with open(
            prediction_file,
            "r",
            encoding="Utf-8",
        ) as file:
            detection = json.load(file)

        # convert the prediction into rbai format for single task
        labels = []
        score_sum = 0
        score_count = 0
        for det in detection["prediction"]:
            (klass, score, x_0, y_0, x_1, y_1) = det
            if score < thresh:
                continue

            score_sum += score
            score_count += 1
            category = taxonomy[int(klass)]
            xnorm = x_0
            ynorm = y_0
            wnorm = x_1 - x_0
            hnorm = y_1 - y_0

            label_entry = {
                "bbox2d": {
                    "xnorm": xnorm,
                    "ynorm": ynorm,
                    "hnorm": hnorm,
                    "wnorm": wnorm,
                },
                "category": [["object", category]],
                "attributes": [],
            }
            labels += [label_entry]

        if score_count == 0:
            score_count = 1
        return_task = {
            "taskId": task["taskId"],
            "priority": 1 - (score_sum / score_count),
            "labels": labels,
        }

        labeled_tasks += [return_task]

    return labeled_tasks


def write_line_to_lst(img_path: str, boxes: np.ndarray, ids: np.ndarray, idx: int):
    """
    Write a single prediction line to .lst file.

    .lst file format: A, B, C, D, E
        A: image index
        B: header length = 2
        C: length of one bbox label = 5
        D: all the bounding box labels
            [class id, xmin, ymin, xmax, ymax]
        E: image path
    """
    header_length = 2
    label_length = 5

    # concat id and bboxes
    labels = np.hstack((ids.reshape(-1, 1), boxes)).astype("float")

    # flatten
    labels = labels.flatten().tolist()
    str_idx = [str(idx)]
    str_header = [str(x) for x in [header_length, label_length]]
    str_labels = [str(x) for x in labels]
    str_path = [img_path]
    line = "\t".join(str_idx + str_header + str_labels + str_path) + "\n"
    return line


def write_image_to_disk(root_dir: str, items: str, presigned_items: str):
    """
    Write image to disk found at presigned_items.

    Parameters
    ------------
    root_dir: str
        root director of path.

    items: str
        Checks if exists within this path, if not creates it.

    presigned_items: str
        The url of the image to download.
    """
    filename = os.path.join(root_dir, items)

    # Create the directory recursively
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Get image data, and write to disk
    if not os.path.exists(filename):
        image = imageio.imread(presigned_items)
        imageio.imwrite(filename, image)


def convert_redbrick_to_sagemaker(  # pylint: disable=too-many-locals
    info: Dict, cache_dir: str
) -> Tuple[Dict[str, int], int]:
    """
    Convert RedBrick labels to sagemaker format.

        - The RedBrick AI json object is first converted into .lst files.
          A single entry in the .lst file is defined in write_to_line_lst.

        - The .lst files are converted to .rec files using the im2rec helper
          function. The .rec file contains both image and label data.
    """
    result = info["labeled"]
    _, taxonomy = create_taxonomy_map(info["taxonomy"]["categories"][0]["children"])

    # clean output directories for images
    os.makedirs(os.path.join(cache_dir, "images"), exist_ok=True)

    train_file = os.path.join(cache_dir, "annotation_redbrick_train.lst")
    val_file = os.path.join(cache_dir, "annotation_redbrick_validation.lst")
    if os.path.exists(train_file):
        os.remove(train_file)
    if os.path.exists(val_file):
        os.remove(val_file)

    train_split = 0.8

    train_idx = 0
    test_idx = 0
    no_labels = 0
    for _, task in enumerate(tqdm.tqdm(result)):
        # skip tasks without labels
        if len(task["labels"]) == 0:
            no_labels += 1
            continue

        # required for creating the record io file
        write_image_to_disk(
            os.path.join(cache_dir, "images"),
            task["items"][0],
            task["itemsPresigned"][0],
        )

        # iterate over labels, compute class_id and store labels
        all_boxes = np.array([])
        all_boxes_ids = np.array([])
        for label_idx, label in enumerate(task["labels"]):

            # compute the class_id
            class_ = label["category"][0][-1]
            class_id = 0
            if class_ in taxonomy:
                class_id = taxonomy[class_]
            else:
                raise ValueError("%s is not part of your taxonomy!" % class_)

            # append box to box_array
            box = np.array(
                [
                    label["bbox2d"]["xnorm"],
                    label["bbox2d"]["ynorm"],
                    label["bbox2d"]["xnorm"] + label["bbox2d"]["wnorm"],
                    label["bbox2d"]["ynorm"] + label["bbox2d"]["hnorm"],
                ]
            )
            if label_idx == 0:
                all_boxes = np.array([box])
            else:
                all_boxes = np.vstack([all_boxes, box])

            # store the corresponding class_id's
            all_boxes_ids = np.append(all_boxes_ids, class_id)

        # split data into test and train, save images
        if np.random.uniform() <= train_split:
            train_list_line = write_line_to_lst(
                os.path.join(cache_dir, "images", task["items"][0]),
                all_boxes,
                all_boxes_ids,
                train_idx,
            )
            train_idx += 1

            # write to lst file
            with open(
                os.path.join(cache_dir, "annotation_redbrick_train.lst"),
                "a+",
                encoding="Utf-8",
            ) as file:
                file.write(train_list_line)

        else:
            test_list_line = write_line_to_lst(
                os.path.join(cache_dir, "images", task["items"][0]),
                all_boxes,
                all_boxes_ids,
                test_idx,
            )
            test_idx += 1

            # write to lst file
            with open(
                os.path.join(cache_dir, "annotation_redbrick_validation.lst"),
                "a+",
                encoding="Utf-8",
            ) as file:
                file.write(test_list_line)

    # create record io files using im2rec
    run_im2rec(
        [
            "--resize",
            "256",
            "--pack-label",
            "--prefix",
            ".redbrick_sagemaker/annotation_redbrick",
            "--root",
            ".",
        ]
    )

    return taxonomy, train_idx
