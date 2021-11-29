import os


class TargetConfig():
    
    def __init__(self):
        self.Host = os.getenv('CRAWLAB_TARGET_HOST')
        self.Port = os.getenv('CRAWLAB_TARGET_PORT')
        self.Username = os.getenv('CRAWLAB_TARGET_USERNAME')
        self.Password = os.getenv('CRAWLAB_TARGET_PASSWORD')
        self.Path = os.getenv('CRAWLAB_TARGET_PATH')
        self.Notify = os.getenv('CRAWLAB_TARGET_NOTIFY')


def get_target_config():
    return TargetConfig()

