# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pytorchyolo', 'pytorchyolo.utils']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.1.0,<9.0.0',
 'imgaug>=0.4.0,<0.5.0',
 'matplotlib>=3.3.3,<4.0.0',
 'numpy>=1.19.5,<2.0.0',
 'tensorboard>=2.4.0,<3.0.0',
 'terminaltables>=3.1.0,<4.0.0',
 'torch>=1.8.1',
 'torchsummary>=1.5.1,<2.0.0',
 'torchvision>=0.8.2',
 'tqdm>=4.55.1,<5.0.0']

entry_points = \
{'console_scripts': ['yolo-detect = pytorchyolo.detect:run',
                     'yolo-test = pytorchyolo.test:run',
                     'yolo-train = pytorchyolo.train:run']}

setup_kwargs = {
    'name': 'pytorchyolo',
    'version': '1.6.1',
    'description': 'Minimal PyTorch implementation of YOLO',
    'long_description': '# PyTorch-YOLOv3\nA minimal PyTorch implementation of YOLOv3, with support for training, inference and evaluation.\n\n[![Ubuntu CI](https://github.com/eriklindernoren/PyTorch-YOLOv3/actions/workflows/main.yml/badge.svg)](https://github.com/eriklindernoren/PyTorch-YOLOv3/actions/workflows/main.yml) [![PyPI pyversions](https://img.shields.io/pypi/pyversions/pytorchyolo.svg)](https://pypi.python.org/pypi/pytorchyolo/) [![PyPI license](https://img.shields.io/pypi/l/pytorchyolo.svg)](LICENSE)\n\n## Installation\n### Installing from source\n\nFor normal training and evaluation we recommend installing the package from source using a poetry virtual environment.\n\n```bash\ngit clone https://github.com/eriklindernoren/PyTorch-YOLOv3\ncd PyTorch-YOLOv3/\npip3 install poetry --user\npoetry install\n```\n\nYou need to join the virtual environment by running `poetry shell` in this directory before running any of the following commands without the `poetry run` prefix.\nAlso have a look at the other installing method, if you want to use the commands everywhere without opening a poetry-shell.\n\n#### Download pretrained weights\n\n```bash\n./weights/download_weights.sh\n```\n\n#### Download COCO\n\n```bash\n./data/get_coco_dataset.sh\n```\n\n### Install via pip\n\nThis installation method is recommended, if you want to use this package as a dependency in another python project.\nThis method only includes the code, is less isolated and may conflict with other packages.\nWeights and the COCO dataset need to be downloaded as stated above.\nSee __API__ for further information regarding the packages API.\nIt also enables the CLI tools `yolo-detect`, `yolo-train`, and `yolo-test` everywhere without any additional commands.\n\n```bash\npip3 install pytorchyolo --user\n```\n\n## Test\nEvaluates the model on COCO test dataset.\nTo download this dataset as well as weights, see above.\n\n```bash\npoetry run yolo-test --weights weights/yolov3.weights\n```\n\n| Model                   | mAP (min. 50 IoU) |\n| ----------------------- |:-----------------:|\n| YOLOv3 608 (paper)      | 57.9              |\n| YOLOv3 608 (this impl.) | 57.3              |\n| YOLOv3 416 (paper)      | 55.3              |\n| YOLOv3 416 (this impl.) | 55.5              |\n\n## Inference\nUses pretrained weights to make predictions on images. Below table displays the inference times when using as inputs images scaled to 256x256. The ResNet backbone measurements are taken from the YOLOv3 paper. The Darknet-53 measurement marked shows the inference time of this implementation on my 1080ti card.\n\n| Backbone                | GPU      | FPS      |\n| ----------------------- |:--------:|:--------:|\n| ResNet-101              | Titan X  | 53       |\n| ResNet-152              | Titan X  | 37       |\n| Darknet-53 (paper)      | Titan X  | 76       |\n| Darknet-53 (this impl.) | 1080ti   | 74       |\n\n```bash\npoetry run yolo-detect --images data/samples/\n```\n\n<p align="center"><img src="https://github.com/eriklindernoren/PyTorch-YOLOv3/raw/master/assets/giraffe.png" width="480"\\></p>\n<p align="center"><img src="https://github.com/eriklindernoren/PyTorch-YOLOv3/raw/master/assets/dog.png" width="480"\\></p>\n<p align="center"><img src="https://github.com/eriklindernoren/PyTorch-YOLOv3/raw/master/assets/traffic.png" width="480"\\></p>\n<p align="center"><img src="https://github.com/eriklindernoren/PyTorch-YOLOv3/raw/master/assets/messi.png" width="480"\\></p>\n\n## Train\nFor argument descriptions have a look at `poetry run yolo-train --help`\n\n#### Example (COCO)\nTo train on COCO using a Darknet-53 backend pretrained on ImageNet run: \n\n```bash\npoetry run yolo-train --data config/coco.data  --pretrained_weights weights/darknet53.conv.74\n```\n\n#### Tensorboard\nTrack training progress in Tensorboard:\n* Initialize training\n* Run the command below\n* Go to http://localhost:6006/\n\n```bash\npoetry run tensorboard --logdir=\'logs\' --port=6006\n```\n\nStoring the logs on a slow drive possibly leads to a significant training speed decrease.\n\nYou can adjust the log directory using `--logdir <path>` when running `tensorboard` and `yolo-train`.\n\n## Train on Custom Dataset\n\n#### Custom model\nRun the commands below to create a custom model definition, replacing `<num-classes>` with the number of classes in your dataset.\n\n```bash\n./config/create_custom_model.sh <num-classes>  # Will create custom model \'yolov3-custom.cfg\'\n```\n\n#### Classes\nAdd class names to `data/custom/classes.names`. This file should have one row per class name.\n\n#### Image Folder\nMove the images of your dataset to `data/custom/images/`.\n\n#### Annotation Folder\nMove your annotations to `data/custom/labels/`. The dataloader expects that the annotation file corresponding to the image `data/custom/images/train.jpg` has the path `data/custom/labels/train.txt`. Each row in the annotation file should define one bounding box, using the syntax `label_idx x_center y_center width height`. The coordinates should be scaled `[0, 1]`, and the `label_idx` should be zero-indexed and correspond to the row number of the class name in `data/custom/classes.names`.\n\n#### Define Train and Validation Sets\nIn `data/custom/train.txt` and `data/custom/valid.txt`, add paths to images that will be used as train and validation data respectively.\n\n#### Train\nTo train on the custom dataset run:\n\n```bash\npoetry run yolo-train --model config/yolov3-custom.cfg --data config/custom.data\n```\n\nAdd `--pretrained_weights weights/darknet53.conv.74` to train using a backend pretrained on ImageNet.\n\n\n## API\n\nYou are able to import the modules of this repo in your own project if you install the pip package `pytorchyolo`.\n\nAn example prediction call from a simple OpenCV python script would look like this:\n\n```python\nimport cv2\nfrom pytorchyolo import detect, models\n\n# Load the YOLO model\nmodel = models.load_model(\n  "<PATH_TO_YOUR_CONFIG_FOLDER>/yolov3.cfg", \n  "<PATH_TO_YOUR_WEIGHTS_FOLDER>/yolov3.weights")\n\n# Load the image as a numpy array\nimg = cv2.imread("<PATH_TO_YOUR_IMAGE>")\n\n# Convert OpenCV bgr to rgb\nimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)\n\n# Runs the YOLO model on the image \nboxes = detect.detect_image(model, img)\n\nprint(boxes)\n# Output will be a numpy array in the following format:\n# [[x1, y1, x2, y2, confidence, class]]\n```\n\nFor more advanced usage look at the method\'s doc strings.\n\n## Credit\n\n### YOLOv3: An Incremental Improvement\n_Joseph Redmon, Ali Farhadi_ <br>\n\n**Abstract** <br>\nWe present some updates to YOLO! We made a bunch\nof little design changes to make it better. We also trained\nthis new network that’s pretty swell. It’s a little bigger than\nlast time but more accurate. It’s still fast though, don’t\nworry. At 320 × 320 YOLOv3 runs in 22 ms at 28.2 mAP,\nas accurate as SSD but three times faster. When we look\nat the old .5 IOU mAP detection metric YOLOv3 is quite\ngood. It achieves 57.9 AP50 in 51 ms on a Titan X, compared\nto 57.5 AP50 in 198 ms by RetinaNet, similar performance\nbut 3.8× faster. As always, all the code is online at\nhttps://pjreddie.com/yolo/.\n\n[[Paper]](https://pjreddie.com/media/files/papers/YOLOv3.pdf) [[Project Webpage]](https://pjreddie.com/darknet/yolo/) [[Authors\' Implementation]](https://github.com/pjreddie/darknet)\n\n```\n@article{yolov3,\n  title={YOLOv3: An Incremental Improvement},\n  author={Redmon, Joseph and Farhadi, Ali},\n  journal = {arXiv},\n  year={2018}\n}\n```\n',
    'author': 'Florian Vahl',
    'author_email': 'git@flova.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eriklindernoren/PyTorch-YOLOv3',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2',
}


setup(**setup_kwargs)
