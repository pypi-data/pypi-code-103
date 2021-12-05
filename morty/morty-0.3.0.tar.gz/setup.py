# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['morty',
 'morty.cli',
 'morty.common',
 'morty.config',
 'morty.dashboard',
 'morty.dashboard.backend',
 'morty.trackers',
 'morty.trainers',
 'morty.utils']

package_data = \
{'': ['*']}

install_requires = \
['Flask>=2.0.2,<3.0.0',
 'click>=8.0.1,<9.0.0',
 'funkybob>=2018.5.1,<2019.0.0',
 'humanfriendly>=10.0,<11.0',
 'rich>=10.11.0,<11.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'typer>=0.4.0,<0.5.0']

extras_require = \
{'tensorflow': ['tensorflow>=2.6.0,<3.0.0'], 'tf': ['tensorflow>=2.6.0,<3.0.0']}

entry_points = \
{'console_scripts': ['morty = morty.cli:main']}

setup_kwargs = {
    'name': 'morty',
    'version': '0.3.0',
    'description': 'TBU',
    'long_description': '# Morty\n\n<img src="https://github.com/roma-glushko/morty/blob/master/img/morty-in-action.png?raw=true" width="600px" />\n\nMorty is a lightweight experiment and configuration manager for small ML/DL projects and Kaggling.\n\nMain Features:\n\n- **Configuration Management**. Morty includes a config loading system based on the python files that makes you configure a wide variety of moving parts quickly and without overheads.\n- **Experiment Management**. Morty provides a flexible, simple and local experiment management system that tracks a lots of context about your project state to make it possible to reproduce experiments.\n\n## Installation\n\n```bash\npip install morty\n# or\npoetry add morty\n```\n\n## Example of Usage\n\nTrains a Keras model on MNIST:\n\n```python\nimport numpy as np\nfrom tensorflow import keras\nfrom tensorflow.keras import layers\n\nfrom morty.config import config, ConfigManager\nfrom morty import ExperimentManager, Experiment\nfrom morty.trainers import TensorflowTrainingTracker\n\n\n@config(path="configs", name="basic_config")\ndef train(configs: ConfigManager) -> None:\n    experiment: Experiment = ExperimentManager(configs=config).create()\n\n    # the data, split between train and test sets\n    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()\n\n    # Scale images to the [0, 1] range\n    x_train = x_train.astype("float32") / 255\n    x_test = x_test.astype("float32") / 255\n\n    # Make sure images have shape (28, 28, 1)\n    x_train = np.expand_dims(x_train, -1)\n    x_test = np.expand_dims(x_test, -1)\n\n    # convert class vectors to binary class matrices\n    y_train = keras.utils.to_categorical(y_train, configs.num_classes)\n    y_test = keras.utils.to_categorical(y_test, configs.num_classes)\n\n    model = keras.Sequential(\n        [\n            keras.Input(shape=configs.image_shape),\n            layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),\n            layers.MaxPooling2D(pool_size=(2, 2)),\n            layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),\n            layers.MaxPooling2D(pool_size=(2, 2)),\n            layers.Flatten(),\n            layers.Dropout(0.5),\n            layers.Dense(configs.num_classes, activation="softmax"),\n        ]\n    )\n\n    model.compile(\n        loss="categorical_crossentropy",\n        optimizer="adam",\n        metrics=("accuracy",),\n    )\n\n    model.summary()\n\n    training_history = model.fit(\n        x_train, y_train,\n        epochs=configs.epochs,\n        batch_size=configs.batch_size,\n        validation_split=configs.val_dataset_fraction,\n        callbacks=(\n            TensorflowTrainingTracker(experiment),\n        )\n    )\n\n    experiment.log_artifact("training_history.pkl", training_history)\n\n    test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)\n\n    print(f"Test loss: {test_loss}")\n    print(f"Test accuracy: {test_accuracy}")\n\n\nif __name__ == "__main__":\n    train()\n```\n\n## Citation\n\nIf Morty helped you to streamline your research, be sure to mention it via the following BibTeX entry:\n\n```\n@Misc{Glushko2021Morty,\n  author =       {Roman Glushko},\n  title =        {Morty - a lightweight experiment and configuration tracking library for small ML/DL projects and Kaggling},\n  howpublished = {Github},\n  year =         {2021},\n  url =          {https://github.com/roma-glushko/morty}\n}\n```\n\n## Acknowledgment\n\n- https://github.com/aimhubio/aim\n- https://devblog.pytorchlightning.ai/introducing-lightningcli-v2-supercharge-your-training-c070d43c7dd6\n- https://github.com/neptune-ai/neptune-client\n- https://github.com/wandb/client/tree/master/wandb\n- https://github.com/allegroai/clearml\n- https://keepsake.ai/\n- https://guild.ai/why-guild/\n- https://metaflow.org/\n- https://github.com/IDSIA/sacred\n\n## Credentials\n\nMade with ❤️ by Roman Glushko (c)',
    'author': 'Roman Glushko',
    'author_email': 'roman.glushko.m@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/roma-glushko/morty',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
