import cv2
import numpy as np
import onnxruntime

from ..utils import preproc, multiclass_nms, demo_postprocess


class PersonDetectionOnnx:
    def __init__(
            self,
            model_file='models/bytetrack_s.onnx',
            input_shape=[608, 1088],
            score_thr=0.2,
            nms_thr=0.7,
            with_p6=False,
    ):
        self.input_shape = input_shape
        self.score_thr = score_thr
        self.nms_thr = nms_thr
        self.with_p6 = with_p6

        self.rgb_means = (0.485, 0.456, 0.406)
        self.std = (0.229, 0.224, 0.225)
        self.session = onnxruntime.InferenceSession(model_file)

    def predict(self, image):
        image, ratio = preproc(image, self.input_shape, self.rgb_means, self.std)
        ort_inputs = {self.session.get_inputs()[0].name: image[None, :, :, :]}
        outputs = self.session.run(None, ort_inputs)
        predictions = demo_postprocess(outputs[0], self.input_shape, p6=self.with_p6)[0]
        boxes = predictions[:, :4]
        scores = predictions[:, 4:5] * predictions[:, 5:]
        boxes_xyxy = np.ones_like(boxes)
        boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.
        boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.
        boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.
        boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.
        boxes_xyxy /= ratio
        dets = multiclass_nms(boxes_xyxy, scores, nms_thr=self.nms_thr, score_thr=self.score_thr)
        return dets[:, :-1]

    def show(self, image, results):
        index = 1
        for (box, score) in zip(list(results[:, :-1].astype(int)), list(results[:, -1])):
            cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (255, 0, 255), 2)
            cv2.putText(image, 'id: %d, score: %.2f' % (index, score),
                        (box[0], box[1] - 4), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), thickness=2)
            index += 1
        return image


if __name__ == '__main__':
    import glob, os, time

    detector = PersonDetectionOnnx()

    img_paths = glob.glob('images/*.jpg')
    for img_path in img_paths:
        img = cv2.imread(img_path)
        s = time.time()
        dets = detector.predict(img)
        print("person detection onnx: ", time.time() - s)
        rimg = detector.show(img, dets)
        filename = os.path.basename(img_path)
        cv2.imwrite('outputs/%s' % filename, rimg)
