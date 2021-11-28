# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydiar', 'pydiar.models', 'pydiar.models.binary_key', 'pydiar.util']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.0,<2.0.0',
 'python_speech_features>=0.6,<0.7',
 'scikit-learn>=1.0.1,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'webrtcvad>=2.0.10,<3.0.0']

setup_kwargs = {
    'name': 'pydiar',
    'version': '0.0.3',
    'description': 'A simple to use library for speaker diarization',
    'long_description': '# PyDiar\n\nThis repo contains simple to use, pretrained/training-less models for speaker diarization.\n\n## Supported Models\n\n- [x] Binary Key Speaker Modeling\n\n  Based on [pyBK](https://github.com/josepatino/pyBK) by Jose Patino which implements the diarization system from "The EURECOM submission to the first DIHARD Challenge" by Patino, Jose and Delgado, Héctor and Evans, Nicholas\n\nIf you have any other models you would like to see added, please open an issue.\n\n## Usage\n\nThis library seeks to provide a very basic interface. To use the Binary Key model on a file, do something like this:\n\n```python\nimport numpy as np\nfrom pydiar.models import BinaryKeyDiarizationModel, Segment\nfrom pydiar.util.misc import optimize_segments\nfrom pydub import AudioSegment\n\nINPUT_FILE = "test.wav"\n\nsample_rate = 32000\naudio = AudioSegment.from_wav(test.wav)\naudio = audio.set_frame_rate(sample_rate)\naudio = audio.set_channels(1)\n\ndiarization_model = BinaryKeyDiarizationModel()\nsegments = diarization_model.diarize(\n    sample_rate, np.array(audio.get_array_of_samples())\n)\noptimized_segments = optimize_segments(segments)\n```\n\nNow `optimized_segments` contains a list of segments with their start, length and speaker id\n\n## Example\n\nA simple script which reads an audio file, diarizes it and transcribes it into the WebVTT format can be found in `examples/generate_webvtt.py`.\nTo use it, download a vosk model from https://alphacephei.com/vosk/models and then run the script using\n\n```shell\npoetry install\npoetry run python -m examples.generate_webvtt -i PATH/TO/INPUT.wav -m PATH/TO/VOSK_MODEL\n```\n',
    'author': 'pajowu',
    'author_email': 'git@ca.pajowu.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/audapolis/pydiar',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
