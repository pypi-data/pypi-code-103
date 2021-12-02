import cv2
import tensorflow as tf
import os
from . import measure
from ..video import vtool
import threading
import random

LOCK = threading.Lock ()
DETECTOR = None
DEFAULT_FACE_SIMILARITY_THRESHOLD = 0.22

def load (pixels, name):
    if pixels.shape [-1] != 3:
        assert name, "Parameter name is required"
        temp = ".{}-temp.bmp".format (name)
        try:
            cv2.imwrite (temp, pixels)
            pixels = cv2.imread (temp)
        finally:
            os.remove (temp)
    return pixels

def initialize_detector ():
    from .mtcnn.mtcnn import MTCNN

    global DETECTOR, LOCK
    with LOCK:
        if DETECTOR is not None:
            return
        DETECTOR = MTCNN ()

def _detect_faces (image):
    initialize_detector ()
    return DETECTOR.detect_faces (image)

def detect (pixels, name = 'face-detector', resize = (48, 48)):
    # crop and strech
    image = load (pixels, name)
    result = _detect_faces (image)
    img = None
    if result:
        result.sort (key = lambda x: x ['box'][3] * x ['box'][2], reverse = True)
        bb = result [0]['box']
        x = max (0, bb [0])
        y = max (0, bb [1])
        crop_img = image [y:y + bb [3], x:x + bb [2]]
        if not resize:
            return result, crop_img
        if resize [0] == -1:
            resize = (int (bb [2] / (bb [3] / resize [1])), resize [1])
        elif resize [1] == -1:
            resize = (resize [0], int (bb [3] / (bb [2] / resize [0])))
        img = cv2.resize (crop_img, resize)
    return result, img

def detect_keep_ratio (pixels, name = 'face-detector', resize = (48, 48)):
    image = load (pixels, name)
    result = _detect_faces (image)
    img = None
    if result:
        result.sort (key = lambda x: x ['box'][3] * x ['box'][2], reverse = True)
        iw, ih = image.shape [:2]
        bb = result [0]['box']
        x = max (0, bb [0])
        y = max (0, bb [1])
        x_ = min (iw, x + bb [2])
        y_ = min (ih, y + bb [3])
        width = x_ - x
        height = y_ - y

        # pad 15%
        y = max (0, y - int (height * 0.06))
        y_ = min (ih, y_ + int (height * 0.06))
        height = y_ - y

        if width > height:
            pad = (width - height) // 2
            y -= pad; y_ += pad
            y = max (0, y); y_ = min (ih, y_)
        else:
            pad = (height - width) // 2
            x -= pad; x_ += pad
            x = max (0, x); x_ = min (iw, x_)

        crop_img = image [y:y_, x:x_]
        if not resize:
            return result, crop_img
        img = cv2.resize (crop_img, resize)
    return result, img

def mark (pixels, name = None):
    image = load (pixels, name)
    result = _detect_faces (image)
    if not result:
        return
    else:
        bounding_box = result [0]['box']
        keypoints = result[0]['keypoints']
        cv2.rectangle (image,
                      (bounding_box[0], bounding_box[1]),
                      (bounding_box[0]+bounding_box[2], bounding_box[1] + bounding_box[3]),
                      (0,155,255),
                      2)
        cv2.circle (image, (keypoints['left_eye']), 2, (0,155,255), 2)
        cv2.circle (image, (keypoints['right_eye']), 2, (0,155,255), 2)
        cv2.circle (image, (keypoints['nose']), 2, (0,155,255), 2)
        cv2.circle (image, (keypoints['mouth_left']), 2, (0,155,255), 2)
        cv2.circle (image, (keypoints['mouth_right']), 2, (0,155,255), 2)
    return image


def from_video_with_metric (video, frame_skip = 10, min_width = 48, min_dist = DEFAULT_FACE_SIMILARITY_THRESHOLD, resize = (48, 48), with_marked = False, choice = 'maxdistance', orientation = 0):
    hashes = []
    faces = []
    hashmap = {}
    markeds = []
    cluster = []
    for idx, pixels in enumerate (vtool.capture (video, frame_skip)):
        if orientation:
            (h, w) = pixels.shape[:2]
            center = (w / 2, h / 2)
            M = cv2.getRotationMatrix2D (center, orientation, 1.0)
            pixels = cv2.warpAffine (pixels, M, (h, w))
        result, img = detect (pixels, resize = resize)
        if not result:
            continue
        bb = result [0]['box']
        if bb [2] < min_width:
            continue
        h = measure.average_hash (img)
        hashmap [id (h)] = (img, pixels, result)

        if choice == "maxdistance":
            dup = False
            for h_ in hashes:
                dist = measure.hamming_dist (h, h_)
                if dist < min_dist:
                    #print ("threshold", dist)
                    dup = True
                    break

            hashes.append (h)
            if not dup:
                faces.append ((result, img))
                if with_marked:
                    markeds.append (mark (pixels))

        elif choice == "all":
            faces.append ((result, img))
            if with_marked:
                markeds.append (mark (pixels))

        elif choice == "single":
            if len (cluster) == 0:
                cluster.append ([h])
                continue

            clustered = False
            for hashes in cluster:
                for h_ in hashes:
                    dist = measure.hamming_dist (h, h_)
                    if dist < min_dist:
                        hashes.append (h)
                        clustered = True
                        break

            if not clustered: # new cluster
                cluster.append ([h])

    def choose (dominent, count = 8):
        if len (dominent) <= 8:
            return dominent
        chosen = []
        th = count / len (dominent)
        for each in dominent:
            if random.random () <= th:
                chosen.append (each)
        return chosen [:count]

    if choice == "single" and cluster:
        dominent = sorted (cluster, key = lambda x: len (x))[-1]
        for h in choose (dominent, 8):
            img, pixels, result = hashmap [id (h)]
            faces.append ((result, img))
            if with_marked:
                markeds.append (mark (pixels))
        #print ('face reducing: {} => {}'.format (len (dominent), len (faces)))

    if with_marked:
        return faces, markeds

    return faces

def from_video (video, frame_skip = 10, min_width = 48, min_dist = DEFAULT_FACE_SIMILARITY_THRESHOLD, resize = (48, 48), with_marked = False, choice = 'maxdistance', orientation = 0):
    faces = from_video_with_metric (video, frame_skip, min_width, min_dist, resize, with_marked, choice, orientation)
    return [img for metric, img in faces]
