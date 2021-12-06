import re
from typing import Union

from tensorflow.keras import Model
from tensorflow.python.keras import backend as K

from .configs import BaseConfig
from ...executors import BaseExecutor


class BaseModel(BaseExecutor, Model):
    """Base models"""

    def __init__(self, pretrained_weights_path: str = None, **kwargs):
        Model.__init__(self, **kwargs)
        BaseExecutor.__init__(self)

        self.pretrained_weights_path = pretrained_weights_path

    def post_init(self):
        self.pre_build()
        # load pre trained weights
        self.load_weights(self.pretrained_weights_path)

    def pre_build(self):
        """If the model has pre trained weights path, then build the model"""
        if self.pretrained_weights_path:
            inputs = self.get_dummy_inputs()  # dumpy inputs
            if not inputs:
                raise ValueError('Unable to load weights into a subclassed BaseModel,'
                                 ' which has not created its variables yet. '
                                 'try to implement `get_dummy_inputs()` first')
            self(inputs)

    def load_weights(self, pretrained_weights_path: str, *args, **kwargs):
        if pretrained_weights_path:
            super(BaseModel, self).load_weights(pretrained_weights_path, *args, **kwargs)

    def get_name_to_variable(self):
        """
        get trainable variables dict, key is variable name, value is resources variable
        """
        import collections
        name_to_variable = collections.OrderedDict()
        for var in self.trainable_variables:
            name = var.name
            m = re.match('^(.*):\\d+$', name)
            if m is not None:
                name = m.group(1)
            name_to_variable[name] = var

        return name_to_variable

    def get_dummy_inputs(self):
        """
        get models inputs
        note:
        if the models need init from pre trained models, it must implement this function
        :return: multi input tensor
        """


class PreTrainModel(BaseModel):
    """Model for pretrained models"""
    config_cls = BaseConfig

    def __init__(self, config: Union[config_cls, str], **kwargs):
        if isinstance(config, str):
            config = self.config_cls(config)
        self.config = config

        super(PreTrainModel, self).__init__(**kwargs)

    def load_weights(self, pretrained_weights_path: str, *args, **kwargs):
        if pretrained_weights_path:
            if not self.built:
                raise ValueError('if you want to restore weights from pretrained, build the model at first.')
            else:
                weight_value_tuples = self.mapping(pretrained_weights_path)
                if not weight_value_tuples:
                    try:
                        super(PreTrainModel, self).load_weights(pretrained_weights_path, *args, **kwargs)
                    except AssertionError:
                        raise NotImplementedError(f'it look like the pre trained model graph doesn\'t match yours, '
                                                  f'try to implement `mapping()` to customize variable-weight mapping.')

                else:
                    K.batch_set_value(weight_value_tuples)

    def mapping(self, pretrained_model_path: str):
        """Return a dict which key is trainable resources, value is pre trained value.
           the tuple like this [(resource_var, value)]
        """
