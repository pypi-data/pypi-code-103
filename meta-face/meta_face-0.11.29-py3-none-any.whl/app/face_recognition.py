import cv2
from ..model_zoo import get_model
from .common import Face


class FaceRecognition:
    def __init__(self, detection_model_path='../models/face_detection.onnx',
                 recognition_model_path='../models/face_recognition.onnx',
                 ctx_id=0):
        self.detector = get_model(name=detection_model_path)
        self.detector.prepare(ctx_id=ctx_id, input_size=(640, 640), det_thresh=0.5)
        self.recognizer = get_model(name=recognition_model_path)
        self.recognizer.prepare(ctx_id=ctx_id)

    def predict(self, image):
        bboxes, kpss = self.detector.detect(image, max_num=0, metric='default')
        if bboxes.shape[0] == 0:
            return []
        faces = []
        for i in range(bboxes.shape[0]):
            bbox = bboxes[i, 0:4]
            det_score = bboxes[i, 4]
            kps = None
            if kpss is not None:
                kps = kpss[i]
            face = Face(bbox=bbox, kps=kps, det_score=det_score)
            self.recognizer.get(image, face)
            faces.append(face)
        return faces

    def compute_similarity(self, feature1, feature2):
        return self.recognizer.compute_sim(feature1, feature2)

    def show(self, image, faces):
        img = image.copy()
        for face in faces:
            box = face.bbox.astype(int)
            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 2)
        return img


if __name__ == '__main__':
    import glob

    app = FaceRecognition()

    img_paths = glob.glob('../images/*.jpg')
    for img_path in img_paths:
        img = cv2.imread(img_path)
        faces = app.predict(img)
        rimg = app.show(img, faces)
        filename = img_path.split('\\')[-1]
        cv2.imwrite('../outputs/%s' % filename, rimg)
