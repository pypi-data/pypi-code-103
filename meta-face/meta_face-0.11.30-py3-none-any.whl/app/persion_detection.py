import cv2
from ..model_zoo import get_model


class PersonDetection:
    def __init__(self, model_path='../models/person_detection.onnx', ctx_id=0):
        self.detector = get_model(name=model_path)
        self.detector.prepare(0, input_size=(640, 640), nms_thresh=0.5)

    def predict(self, image):
        boxes, _ = self.detector.detect(image)
        return boxes.astype(int)

    def show(self, image, boxes):
        img = image.copy()
        for box in boxes:
            cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (255, 255, 0), 2)
        return img


if __name__ == '__main__':
    import glob

    detector = PersonDetection()

    img_paths = glob.glob('../images/*.jpg')
    for img_path in img_paths:
        img = cv2.imread(img_path)
        faces = detector.predict(img)
        rimg = detector.show(img, faces)
        filename = img_path.split('\\')[-1]
        cv2.imwrite('../outputs/%s' % filename, rimg)
