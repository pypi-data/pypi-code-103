import json


class BaseConfig:
    """Base Config"""

    def __init__(self, config_path, name='base', *args, **kwargs):
        with open(config_path, 'r', encoding='utf-8') as f:
            paras = json.load(f)
            self.__dict__.update(paras)
        self.name = name

    def save_config(self, save_path: str = None):
        """
        Save configs
        :param save_path: save path
        :return:
        """
        if not save_path:
            save_path = f'{self.name}.json'
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=4)


class BertConfig(BaseConfig):
    """Config for Bert"""

    def __init__(self, *args, **kwargs):
        super().__init__(name='bert', *args, **kwargs)


class ElectraConfig(BaseConfig):
    """Config for Electra"""

    def __init__(self, *args, **kwargs):
        super().__init__(name='electra', *args, **kwargs)


class GPTConfig(BaseConfig):
    """Config for GPT"""

    def __init__(self, *args, **kwargs):
        super().__init__(name='gpt', *args, **kwargs)


class HuaweiGPTConfig(BaseConfig):
    """Config for GPT"""

    def __init__(self, *args, **kwargs):
        super().__init__(name='huawei_gpt', *args, **kwargs)


class SoftMaskedBertConfig(BaseConfig):
    """
    Soft Masked Bert Config
    """

    def __init__(self, *args, **kwargs):
        super(SoftMaskedBertConfig, self).__init__(name='soft_masked_bert', *args, **kwargs)
