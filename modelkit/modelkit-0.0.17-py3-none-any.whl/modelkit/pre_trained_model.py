#  Without asset

# In [13]: mm.saved_model.signatures["serving_default"].output_dtypes
# Out[13]: {'outputs': tf.float32}

# In [14]: mm.saved_model.signatures["serving_default"].output_shapes
# Out[14]: {'outputs': TensorShape([None, 512])}


#  https://tfhub.dev/google/universal-sentence-encoder-multilingual/3

import numpy as np
import tensorflow_text

import modelkit
from modelkit.core.models.tensorflow_model import TensorflowModel


class USEModel(TensorflowModel):
    CONFIGURATIONS = {"use": {}}

    def __init__(self, **kwargs):
        import pdb

        pdb.set_trace()
        super().__init__(
            output_tensor_mapping={"outputs": "Identity:0"},
            output_shapes={"outputs": (512,)},
            output_dtypes={"outputs": np.float32},
            asset_path="/Users/tgenin/data/pretrained",
            **kwargs,
        )


class USEModel2(TensorflowModel):
    CONFIGURATIONS = {
        "use2": {
            "model_settings": {
                "output_tensor_mapping": {"outputs": "Identity:0"},
                "output_shapes": {"outputs": (512,)},
                "output_dtypes": {"outputs": np.float32},
            }
        }
    }

    def __init__(self, **kwargs):
        super().__init__(asset_path="/Users/tgenin/data/pretrained", **kwargs)


class USEModel3(TensorflowModel):
    CONFIGURATIONS = {
        "use3": {
            "asset": "aa",
            "model_settings": {
                "output_tensor_mapping": {"outputs": "Identity:0"},
                "output_shapes": {"outputs": (512,)},
                "output_dtypes": {"outputs": np.float32},
                "asset_path": "/Users/tgenin/data/pretrained",
            },
        }
    }


modelkit.load_model("use2", models=USEModel2)

modelkit.load_model("use", models=USEModel)


model_library = modelkit.ModelLibrary(
    required_models={
        "use2": {"asset_path": "/Users/tgenin/data/pretrained"},
    },
    models=USEModel2,
)
mm = model_library.get("use2")


#  with asset

#  ./bin/cli.py assets new ~/data/pretrained/ local_asset/use --storage-prefix assets-v3-override


import tensorflow_text

import modelkit
from modelkit.core.models.tensorflow_model import TensorflowModel


class USEModel(TensorflowModel):
    CONFIGURATIONS = {"use": {}}

    def __init__(self, **kwargs):
        super().__init__(
            output_tensor_mapping={"outputs": "Identity:0"},
            output_shapes={"outputs": (512,)},
            output_dtypes={"outputs": np.float32},
            asset_path="/Users/tgenin/data/pretrained",
            **kwargs,
        )
