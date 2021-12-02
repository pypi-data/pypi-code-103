from bbcloud_python_sdk.Api.Models.Model import Model


class Artifacts(Model):
    def __init__(self, *args, **kwargs):
        super(Artifacts, self).__init__(*args, **kwargs)
        self._modal_path = 'artifact/artifacts'
