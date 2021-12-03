# Copyright 2020 Tobias Höfer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""Implements the yolov2 loss."""
import math

import tensorflow as tf


def yolo_loss(y_true,
              y_pred,
              anchors,
              lambda_coord=1.0,
              lambda_obj=5.0,
              lambda_noobj=1.0,
              lambda_class=1.0,
              iou_threshold=0.4,
              step=0,
              is_training=True,
              version="ciou"):
    """Defines the yolov2 multipart loss function.

    Args:
        y_true (tensor): Label form:
            (BS, GRID, GRID, ANCHORS, (x1, y1, width, height, obj, cls_idx)
        y_pred ([type]): Model output:
            (BS,GRID,GRID,ANCHORS,(x,y,w,h,objectivness,n_classes))
        anchors
        step (int): For tensorbaord output.

    Returns:
        loss (scalar): weighted yolov2 loss.
    """
    batch_size = tf.shape(y_pred)[0]
    grid_h = tf.shape(y_pred)[1]
    grid_w = tf.shape(y_pred)[2]
    boxes = tf.shape(y_pred)[3]

    # Extract model output.
    # We use a grid cell scale instead of pixel values. This bounds the
    # predicton to a specific cell (localization) and helps with numerical
    # stability. Since we constrain the location prediction (pixel values
    # could be anywehere) the parametrization is easier to learn, making the
    # network more stable. Different scales can be implemented here.
    grid_coord = yolo_grid(batch_size, grid_h, grid_w, boxes)
    p_box_xy, p_box_wh, p_box_conf, p_box_class = extract_model_output(
        y_pred, grid_coord, anchors)

    # Extract ground truth output.
    true_box_xy, true_box_wh, true_box_conf, true_box_class = extract_label(
        y_true)

    # Calculate coordinate loss_xywh.
    loss_xywh = None
    if version == "vanilla":
        loss_xywh = _loss_xywh(
            true_box_xy,
            p_box_xy,
            true_box_wh,
            p_box_wh,
            true_box_conf,
            lambda_coord,
        )
    elif version == "ciou":
        loss_xywh = _cIoU_loss(true_box_xy, p_box_xy, true_box_wh, p_box_wh,
                               true_box_conf)

    # Calculate loss for the class probabilities.
    loss_class = _loss_class(
        true_box_class,
        p_box_class,
        true_box_conf,
        lambda_class,
    )

    pred = tf.concat([p_box_xy, p_box_wh, p_box_conf, p_box_class], axis=-1)

    # Calcculate IOUs where object exists.
    iou_scores = _calculate_ious(y_true, pred)
    # Calcculate max IOUs TODO
    num_true_labels = grid_h * grid_w * boxes
    y_true_p = tf.reshape(y_true[..., :4],
                          shape=(batch_size, 1, 1, 1, num_true_labels, 4))

    # (bs, grid, grid, boxes, num_true_labels)
    iou_scores_buff = _calculate_ious(y_true_p, tf.expand_dims(y_pred, axis=4))
    max_iou_scores = tf.argmax(iou_scores_buff, axis=4)

    loss_conf = _loss_conf(true_box_conf, p_box_conf, iou_scores,
                           max_iou_scores, lambda_obj, lambda_noobj,
                           iou_threshold)

    # Combine all three loss parts
    loss = loss_xywh + loss_class + loss_conf

    if is_training:
        tf.summary.scalar("loss_xywh", loss_xywh, step=step)
        tf.summary.scalar("loss_class", loss_class, step=step)
        tf.summary.scalar("loss_conf", loss_conf, step=step)
        tf.summary.scalar("total_loss", loss, step=step)
    return loss


def yolo_grid(batch_size, grid_h, grid_w, boxes):
    """Ouputs yolo grid coordinates to use as cx, cy offsets from top left
    corner.

    Example of batch_size 1 and grid 2x2 and 1 anchors boxes.

        -----------------------
        -          -          -
        -   (0,0)  -   (0,1)  -
        -          -          -
        -----------------------
        -          -          -
        -   (1,0)  -   (1,1)  -
        -          -          -
        -----------------------

    Args:
        batch_size (int): Number of batches.
        grid (int): Grid.
        boxes (int): Number of different anchor boxes.

    Returns:
        [Tensor]: Coordinate grid values.
    """
    # TODO eval
    cell_x = tf.cast(tf.reshape(tf.tile(tf.range(grid_w), [grid_h]),
                                (1, grid_h, grid_w, 1, 1)),
                     dtype=tf.float32)

    # TODO non symmetrie
    cell_y = tf.transpose(cell_x, (0, 2, 1, 3, 4))
    ## cell_gird.shape = (16, 13, 13, 5, 2)
    ## for any n, k, i, j
    ##    cell_grid[n, i, j, anchor, k] = j when k = 0
    ## for any n, k, i, j
    ##    cell_grid[n, i, j, anchor, k] = i when k = 1
    cell_grid = tf.tile(tf.concat([cell_x, cell_y], -1),
                        [batch_size, 1, 1, boxes, 1])

    return cell_grid


def extract_model_output(y_pred, grid_coord, anchors):
    """Extract loss specific yolov2 values from model output.

    Args:
        y_pred (Tensor): Yolov2 specific format:
            (BS, GRIDW, GRIDH, BOXES, 5 + CLASSES)
        grid_coord (Tensor): Grid coordinates as cluster centroids.
        anchors (list): List of all anchor widths and heights (Priors).

    Returns:
        box_xy: (tx, ty) -> Center coordinates of object midpoints.
            (BS, GRIDW, GRIDH, BOXES, 2)
        box_wh: (tw, th) -> Anchor box prior offsets.
            (BS, GRIDW, GRIDH, BOXES, 2)
        box_conf: Box confidence values.
            (BS, GRIDW, GRIDH, BOXES, 1)
        box_class: Unprocessed conditional Class probabilities.
            (BS, GRIDW, GRIDH, BOXES, num_classes)
    """
    # Number of anchor boxes.
    boxes = tf.shape(y_pred)[3]

    # Unrestricted xy object midpoints (center coords) (tx, ty).
    box_xy = y_pred[..., 0:2]
    # Direct location prediction!
    # bx = sig(tx) + cx <- Grid cell offset from top left
    # by = sig(ty) + cy <- Grid cell offset from top left
    # YOLOv4: Grid Sensitivity!
    # For cases bx = cx (sig(tx)->0) and bx = cx+1 (sig(tx)->1)tx needs to have
    # huge neg or pos value multiplying with a scaling factor makes this easier
    # -> PP-YOLO.
    scale_x_y = 1.05
    xy_grid_sensitiv = tf.cast(tf.sigmoid(box_xy), dtype=tf.float32) * \
        scale_x_y - (scale_x_y-1)/2
    box_xy = xy_grid_sensitiv + grid_coord

    # Unrestricted w, h values.
    box_wh = y_pred[..., 2:4]
    # Make w, h strictly positive values. TODO check
    box_wh = tf.cast(tf.exp(box_wh), dtype=tf.float32) * tf.cast(
        tf.reshape(anchors, [1, 1, 1, boxes, 2]), dtype=tf.float32)

    # Restrict box_confidence values to [0, 1].
    # Shape (bs, grid, grid, anchors, 1)

    box_conf = tf.sigmoid(y_pred[..., 4:5])
    # Unrestricted conditional class probabilities: [pC1, pC2....pCn] ->
    # Later input to softmax, so no neccessary processing here.
    box_classes = y_pred[..., 5:]

    return box_xy, box_wh, box_conf, box_classes


def extract_label(y_true, only_class_index=False):
    """Extract loss specific yolov2 values from label.

    Args:
        y_true (Tensor): Yolov2 specific format:
            (BS, GRIDW, GRIDH, BOXES, 5 + CLASSES)

    Returns:
        box_xy: x, y coordinates for every anchor box in every grid cell.
            (BS, GRIDW, GRIDH, BOXES, box_xy)
        box_wh: w, h for every anchor box in every grid cell.
            (BS, GRIDW, GRIDH, BOXES, box_wh)
        box_conf: Confidence values for every anchor box in every grid cell.
            (BS, GRIDW, GRIDH, BOXES, box_conf)
        box_class: Class index for every anchor box in every grid cell.
            (BS, GRIDW, GRIDH, BOXES, box_class)
    """
    box_xy = y_true[..., 0:2]
    box_wh = y_true[..., 2:4]
    box_conf = y_true[..., 4:5]
    # Only class index.
    if only_class_index:
        box_class = tf.argmax(y_true[..., 5:], -1)
    else:
        box_class = y_true[..., 5:]
    return box_xy, box_wh, box_conf, box_class


def _loss_xywh(true_box_xy, pred_box_xy, true_box_wh, pred_box_wh,
               true_box_conf, lambda_coord):
    """Calculates the mean squared error between predicted and true object
    center points. In addition use mean squared error between square root of
    bounding box widths and heights offsets to prior anchor boxes. Reason: Small
    deviations in large boxes matter less than in small boxes.

    This function uses a 0/1 indicator function to only compare values
    if and only if box confidence=1 in true_box_confidence.

    Args:
        true_box_xy ([type]): [description]
        pred_box_xy ([type]): [description]
        true_box_wh ([type]): [description]
        pred_box_wh ([type]): [description]
        true_box_conf ([type]): [description]
        lambda_coord ([type]): [description]

    Returns:
        [type]: [description]
    """
    # 1/0 Indicator function: L_{i,j}^{obj} indicates if object is present else
    # 0.
    # We only compare results if an object is present in the cell.
    # (BS, GRID,GRID,BOXES,1)
    # This mask also weighs the loss term with lambda_coord (hyperparameter).
    # 1/0 Indicator function: L_{i,j}^{obj} indicates if object is present else
    # 0.
    # We only compare results if an object is present in the cell.
    # (BS, GRID,GRID,BOXES,1)
    # This mask also weighs the loss term with lambda_coord (hyperparameter).
    coord_mask = tf.cast(true_box_conf * lambda_coord, dtype=tf.float32)
    loss_xy = tf.reduce_sum(
        tf.square(
            tf.cast(true_box_xy, dtype=tf.float32) -
            tf.cast(pred_box_xy, dtype=tf.float32)) *
        tf.cast(coord_mask, dtype=tf.float32))
    # Use sqrt of width and height to weigh small deviations in large boxes
    # less than in small boxes.
    loss_wh = tf.reduce_sum(
        tf.square(
            tf.cast(tf.sqrt(true_box_wh), dtype=tf.float32) -
            tf.cast(tf.sqrt(pred_box_wh), dtype=tf.float32)) * coord_mask)

    loss_xywh = (loss_xy + tf.cast(loss_wh, dtype=tf.float32))
    return loss_xywh


def _cIoU_loss(true_box_xy, pred_box_xy, true_box_wh, pred_box_wh,
               true_box_conf):
    """Computes the CIoU Localization Loss
    Inspired by: https://github.com/robbebluecp/tf2-yolov4/blob/online/loss.py
    """
    b1_xy = true_box_xy
    b1_wh = true_box_wh
    b1_wh_half = b1_wh / 2.
    b1_mins = b1_xy - b1_wh_half
    b1_maxes = b1_xy + b1_wh_half

    b2_xy = pred_box_xy
    b2_wh = pred_box_wh
    b2_wh_half = b2_wh / 2.
    b2_mins = b2_xy - b2_wh_half
    b2_maxes = b2_xy + b2_wh_half

    intersect_mins = tf.keras.backend.maximum(b1_mins, b2_mins)
    intersect_maxes = tf.keras.backend.minimum(b1_maxes, b2_maxes)
    intersect_wh = tf.keras.backend.maximum(intersect_maxes - intersect_mins,
                                            0.)
    intersect_area = intersect_wh[..., 0] * intersect_wh[..., 1]
    b1_area = b1_wh[..., 0] * b1_wh[..., 1]
    b2_area = b2_wh[..., 0] * b2_wh[..., 1]
    union_area = b1_area + b2_area - intersect_area
    # calculate IoU, add epsilon in denominator to avoid dividing by 0
    iou = intersect_area / (union_area + tf.keras.backend.epsilon())

    # box center distance
    center_distance = tf.keras.backend.sum(tf.keras.backend.square(b1_xy -
                                                                   b2_xy),
                                           axis=-1)
    # get enclosed area
    enclose_mins = tf.keras.backend.minimum(b1_mins, b2_mins)
    enclose_maxes = tf.keras.backend.maximum(b1_maxes, b2_maxes)
    enclose_wh = tf.keras.backend.maximum(enclose_maxes - enclose_mins, 0.0)
    # get enclosed diagonal distance
    enclose_diagonal = tf.keras.backend.sum(
        tf.keras.backend.square(enclose_wh), axis=-1)
    # calculate DIoU, add epsilon in denominator to avoid dividing by 0
    diou = 1 - iou + center_distance / \
        (enclose_diagonal + tf.keras.backend.epsilon())

    v = 4 * tf.keras.backend.square(
        tf.math.atan2(b1_wh[..., 0], b1_wh[..., 1]) -
        tf.math.atan2(b2_wh[..., 0], b2_wh[..., 1])) / (math.pi * math.pi)
    alpha = v / (1.0 - iou + v)
    ciou = diou + alpha * v

    ciou = tf.expand_dims(ciou, -1)
    ciou = tf.cast(ciou, dtype=tf.float32)
    coord_mask = tf.cast(true_box_conf, dtype=tf.float32)

    ciou = tf.keras.backend.sum(ciou * coord_mask)
    return ciou


def _loss_class(
        true_box_class,
        p_box_class,
        true_box_conf,
        lambda_class,
):
    """[summary]

    Args:
        true_box_class ([type]): [description]
        p_box_class ([type]): [description]
        true_box_conf ([type]): [description]
        lambda_class ([type]): [description]

    Returns:
        [type]: [description]
    """
    # Indicator function to only weigh class predictions if an object exists.
    class_mask = true_box_conf * lambda_class
    # Use xentropy between class probabilities.
    #loss_class = tf.nn.sparse_softmax_cross_entropy_with_logits(
    #    labels=true_box_class, logits=p_box_class)
    # Use binary cross entropy for class prediction. Introduced in YOLOv3
    # Softmax is not neccessary for good performance and hinders some data
    # distribution with overlapping laberls (i.e. Woman and Person).
    # A multilabel approach better models the data.
    loss_class = tf.nn.sigmoid_cross_entropy_with_logits(labels=true_box_class,
                                                         logits=p_box_class)
    loss_class = tf.reduce_sum(
        tf.cast(loss_class, dtype=tf.float32) *
        tf.cast(class_mask, dtype=tf.float32))
    return loss_class


def _calculate_ious(A1, A2):
    def process_boxes(A):
        # ALign x-w, y-h
        A_xy = tf.cast(A[..., 0:2], dtype=tf.float32)
        A_wh = tf.cast(A[..., 2:4], dtype=tf.float32)

        A_wh_half = A_wh / 2.
        # Get x_min, y_min
        A_mins = tf.cast(A_xy - A_wh_half, dtype=tf.float32)
        # Get x_max, y_max
        A_maxes = tf.cast(A_xy + A_wh_half, dtype=tf.float32)

        return A_mins, A_maxes, A_wh

    # Process two sets
    A2_mins, A2_maxes, A2_wh = process_boxes(A2)
    A1_mins, A1_maxes, A1_wh = process_boxes(A1)

    # Intersection as min(Upper1, Upper2) - max(Lower1, Lower2)
    intersect_mins = tf.math.maximum(A2_mins, A1_mins)
    intersect_maxes = tf.math.minimum(A2_maxes, A1_maxes)

    # Getting the intersections in the xy (aka the width, height intersection)
    intersect_wh = tf.math.maximum(intersect_maxes - intersect_mins, 0.)

    # Multiply to get intersecting area
    intersect_areas = intersect_wh[..., 0] * intersect_wh[..., 1]

    # Values for the single sets
    true_areas = A1_wh[..., 0] * A1_wh[..., 1]
    pred_areas = A2_wh[..., 0] * A2_wh[..., 1]

    # Compute union for the IoU
    union_areas = pred_areas + true_areas - intersect_areas
    return intersect_areas / union_areas


def _loss_conf(true_box_conf, p_box_conf, iou_scores, max_iou_scores,
               lambda_obj, lambda_noobj, iou_threshold):
    """Two part loss function.
    """
    # Indicator function for existing objects.
    #
    #          / 1 if confidence(i,j) = 1
    # L_obj =
    #          \ 0 else
    # TODO bs=1 not supported
    mask_obj = tf.squeeze(true_box_conf) * lambda_obj

    # Indicator function for non-existing objects. L_noobj.
    #
    #          / 1 if maxIOU < threshold and confidence(i,j) = 0
    # L_noobj =
    #          \ 0 else
    #
    mask_noobj = tf.cast(
        (tf.cast(max_iou_scores, dtype=tf.float32) < tf.cast(
            iou_threshold, dtype=tf.float32)),
        dtype=tf.float32) * tf.cast(
            (1 - tf.squeeze(true_box_conf)), dtype=tf.float32) * lambda_noobj

    mask_confidence = tf.cast(mask_obj, dtype=tf.float32) + mask_noobj

    loss = tf.keras.backend.sum(
        tf.math.square(iou_scores - tf.squeeze(p_box_conf)) * mask_confidence)

    return loss
