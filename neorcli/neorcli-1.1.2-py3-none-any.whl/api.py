from functools import wraps

import requests

BACKEND_URL = 'https://api.neorcloud.com'


def api_exception_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            print(func.__name__, e.response.json())

    return wrapper


class APIClient:
    def __init__(self, token, base_url=BACKEND_URL):
        self.token = token
        self.base_url = base_url

    @api_exception_wrapper
    def fetch_service(self, service_id):
        url = f'{BACKEND_URL}/operations/services/{service_id}/'
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    @api_exception_wrapper
    def fetch_image(self, image_id):
        url = f'{BACKEND_URL}/operations/images/{image_id}/'
        headers = {'Authorization': f'Token {self.token}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    @api_exception_wrapper
    def create_image(self, tag, previous_image, base_image_id=None, branch=None):
        url = f'{BACKEND_URL}/operations/images/'
        headers = {'Authorization': f'Token {self.token}'}
        data = {
            'title': previous_image['title'],
            'project_id': previous_image['project_id'],
            'preset_id': previous_image['preset']['id'],
            'tag': tag,
            'git_url': previous_image['git_url'],
            'git_branch': branch or previous_image['git_branch'],
            'build_envs': previous_image['build_envs'],
            'init_command': previous_image['init_command'],
            'startup_command': previous_image['startup_command'],
            'daemon_command': previous_image['daemon_command'],
        }
        if base_image_id:
            data['base_image_id'] = base_image_id
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    @api_exception_wrapper
    def patch_service(self, service_id, image_id):
        url = f'{BACKEND_URL}/operations/services/{service_id}/'
        headers = {'Authorization': f'Token {self.token}'}
        data = {
            'image_id': image_id
        }
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    @api_exception_wrapper
    def create_pipeline(self, project_id, services, images, base_image_id=None):
        url = f'{BACKEND_URL}/operations/pipelines/'
        headers = {'Authorization': f'Token {self.token}'}
        data = {
            'project_id': project_id,
            'services': services,
            'images': images
        }
        if base_image_id:
            data['base_image_id'] = base_image_id
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
