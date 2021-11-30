#  with asset

#  ./bin/cli.py assets new ~/data/pretrained/ local_asset/use
#  ./bin/cli.py assets new ~/data/pretrained/ local_asset/use --storage-prefix assets-v3-override

import numpy as np
import tensorflow_text

from modelkit.core.models.tensorflow_model import TensorflowModel


class USEModel(TensorflowModel):
    CONFIGURATIONS = {
        "use": {
            "asset": "my_assets/use:0.0",
            "model_settings": {
                "output_tensor_mapping": {"outputs": "Identity:0"},
                "output_shapes": {"outputs": (512,)},
                "output_dtypes": {"outputs": np.float32},
            },
        }
    }


# class USEModel(TensorflowModel):
#     #  CONFIGURATIONS = {"use": {"asset": "local_asset/use:0.0"}}
#     CONFIGURATIONS = {"use": {"asset": "local_asset/use"}}

#     def __init__(self, **kwargs):
#         super().__init__(
#             output_tensor_mapping={"outputs": "Identity:0"},
#             output_shapes={"outputs": (512,)},
#             output_dtypes={"outputs": np.float32},
#             **kwargs,
#         )


# import tensorflow
# import modelkit.use
#  mm = modelkit.load_model("use", models=modelkit.use)
#  ./bin/cli.py tf-serving local-docker modelkit.use -r "use"
#  docker run --name local-tf-serving -d -p 8500:8500 -p 8501:8501 -v ${MODELKIT_ASSETS_DIR}:/config -t tensorflow/serving --model_config_file=/config/config.config --rest_api_port=8501 --port=8500

#  MODELKIT_TF_SERVING_ENABLE=1 ipython
