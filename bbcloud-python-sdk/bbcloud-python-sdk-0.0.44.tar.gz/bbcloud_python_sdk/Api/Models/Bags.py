from bbcloud_python_sdk.Api.Models.Model import Model


class Bags(Model):
    def __init__(self, *args, **kwargs):
        super(Bags, self).__init__(*args, **kwargs)
        self._modal_path = 'bag/bags'
