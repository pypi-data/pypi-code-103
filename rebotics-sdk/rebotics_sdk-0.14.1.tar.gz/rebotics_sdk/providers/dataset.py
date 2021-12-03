import logging

from .base import ReboticsBaseProvider, remote_service

logger = logging.getLogger(__name__)


class DatasetProvider(ReboticsBaseProvider):
    @remote_service('/api/v1/')
    def api_root(self):
        return self.session.get()

    @remote_service('/api/v1/token-auth/')
    def token_auth(self, username, password, verification_code=None):
        payload = dict(
            username=username,
            password=password,
        )
        if verification_code is not None:
            payload['verification_code'] = verification_code

        json_data = self.session.post(data=payload)
        self.headers['Authorization'] = 'Token %s' % json_data['token']
        return json_data

    @remote_service('/api/v1/import_training_data/', timeout=10000)
    def import_training_data(self, data):
        return self.session.post(json=data)

    @remote_service('/api/v1/detection-images/{id}/')
    def get_detection_image_by_id(self, image_id):
        return self.session.get(id=image_id)
