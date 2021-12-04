import cv2
import torch
import torch.nn as nn
from ..model_zoo import YOLOPAFPN, YOLOX, YOLOXHead
from ..utils import get_exp_by_file, preproc, postprocess


class PersonDetection:
    def __init__(
            self,
            model_file='models/model_trt.pth',
            exp_file='configs/yolox_s_mix_det.py',
            device='gpu',
            use_trt=True,
            use_fp16=False
    ):
        device = torch.device("cuda" if device == "gpu" else "cpu")
        exp = get_exp_by_file(exp_file)
        model = self.get_model(exp).to(device)
        model.eval()

        if not use_trt:
            ckpt = torch.load(model_file, map_location="cpu")
            model.load_state_dict(ckpt["model"])

        if use_fp16: model = model.half()

        if use_trt:
            model.head.decode_in_inference = False
            decoder = model.head.decode_outputs
        else:
            decoder = None

        self.model = model
        self.decoder = decoder
        self.num_classes = exp.num_classes
        self.confthre = exp.test_conf
        self.nmsthre = exp.nmsthre
        self.test_size = exp.test_size
        self.device = device
        self.fp16 = use_fp16

        if use_trt:
            from torch2trt import TRTModule

            model_trt = TRTModule()
            model_trt.load_state_dict(torch.load(model_file))
            x = torch.ones(1, 3, exp.test_size[0], exp.test_size[1], device=device)
            self.model(x)
            self.model = model_trt
        self.rgb_means = (0.485, 0.456, 0.406)
        self.std = (0.229, 0.224, 0.225)

    def get_model(self, exp):
        def init_yolo(M):
            for m in M.modules():
                if isinstance(m, nn.BatchNorm2d):
                    m.eps = 1e-3
                    m.momentum = 0.03

        if getattr(self, "model", None) is None:
            in_channels = [256, 512, 1024]
            backbone = YOLOPAFPN(exp.depth, exp.width, in_channels=in_channels)
            head = YOLOXHead(exp.num_classes, exp.width, in_channels=in_channels)
            model = YOLOX(backbone, head)

        model.apply(init_yolo)
        model.head.initialize_biases(1e-2)
        return model

    def predict(self, image):
        image, ratio = preproc(image, self.test_size, self.rgb_means, self.std)
        image = torch.from_numpy(image).unsqueeze(0).float().to(self.device)
        if self.fp16: image = image.half()

        with torch.no_grad():
            outputs = self.model(image)
            if self.decoder is not None:
                outputs = self.decoder(outputs, dtype=outputs.type())
            outputs = postprocess(outputs, self.num_classes, self.confthre, self.nmsthre)

        return outputs


if __name__ == '__main__':
    import glob, time

    detector = PersonDetection()

    img_paths = glob.glob('images/*.jpg')
    for img_path in img_paths:
        img = cv2.imread(img_path)
        s = time.time()
        results = detector.predict(img)
        print("person detection: ", time.time() - s)
        print(results[0].shape)
