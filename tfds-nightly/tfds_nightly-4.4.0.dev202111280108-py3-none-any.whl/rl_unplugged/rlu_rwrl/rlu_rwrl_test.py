# coding=utf-8
# Copyright 2021 The TensorFlow Datasets Authors.
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

"""rlu_rwrl dataset."""

import tensorflow_datasets.public_api as tfds
from tensorflow_datasets.rl_unplugged.rlu_rwrl import rlu_rwrl


class RluRwrlTest(tfds.testing.DatasetBuilderTestCase):
  """Tests for rlu_rwrl dataset."""
  DATASET_CLASS = rlu_rwrl.RluRwrl
  SPLITS = {
      'train': 1,  # Number of fake train example
  }

  SKIP_TF1_GRAPH_MODE = True

  # The different configs are only different in the name of the files.
  BUILDER_CONFIG_NAMES_TO_TEST = [
      'cartpole_swingup_combined_challenge_none_1_percent'
  ]

  @classmethod
  def setUpClass(cls):
    rlu_rwrl.RluRwrl._INPUT_FILE_PREFIX = cls.dummy_data
    rlu_rwrl.RluRwrl._SHARDS = 1
    super().setUpClass()


if __name__ == '__main__':
  tfds.testing.test_main()
