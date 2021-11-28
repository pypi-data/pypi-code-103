import os
import sys

import pytest

# テスト対象のファイルへのパスを通している
# pytestの設定
PARENT_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
SOURCE_PATH = PARENT_PATH.rsplit("/", 1)[0]
print(f"test_target_path:= {SOURCE_PATH}")
sys.path.append(f"{SOURCE_PATH}")

# テスト対象のディレクトリに移動
os.chdir("./kabutobashi")

# skip if: https://thinkami.hatenablog.com/entry/2017/10/25/222551

DATA_PATH = f"{SOURCE_PATH}/data"


@pytest.fixture
def data_path():
    yield DATA_PATH
