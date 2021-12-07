#
#  This is the configuration file that allows to configure values that are
# required to access various S3 stores.
#
# If you want to add a S3 store that is not available as an entry, yet:
#   - create a new (unique!) key within the TYPES dict
#   - add a dict as value to the key, holding the same keys (all of them!)
#     as there are in the existing ones
#   - enter a default endpoint, and
#   - a region (if the new S3 store supports regions)
#   - if the S3 store has regions, add the new key to the REGIONREQUIRED list
#

# the TYPES dict describes the parameters that are used in .hs3sh.conf:
TYPES = {'aws': {'comment': '',
                 'endpoint': 's3.amazonaws.com',
                 'region': 'us-east-1',
                 'https': True,
                 'port': 443,
                 'signature_version': 's3v4',
                 'payload_signing_enabled': True,
                 'aws_access_key_id': '',
                 'aws_secret_access_key': ''
                 },
         'cloudian': {'comment': '',
                      'endpoint': 'cloudian.your.domain',
                      'region': 's3-region',
                      'https': True,
                      'port': 443,
                      'aws_access_key_id': '',
                      'aws_secret_access_key': ''
                      },
         'ecs': {'comment': '',
                 'endpoint': 'namespace.ecs.your.domain',
                 'region': '',
                 'https': True,
                 'port': 9021,
                 'aws_access_key_id': '',
                 'aws_secret_access_key': ''
                 },
         'hs3': {'comment': '',
                 'endpoint': 'tenant.hcp.your.domain',
                 'region': '',
                 'https': True,
                 'port': 443,
                 'signature_version': 's3v4',
                 'payload_signing_enabled': True,
                 'aws_access_key_id': '',
                 'aws_secret_access_key': ''
                 },
         'compatible': {'comment': '',
                        'endpoint': 'whatever.your.domain',
                        'region': '',
                        'https': True,
                        'port': 443,
                        'aws_access_key_id': '',
                        'aws_secret_access_key': ''
                        },
         }

# these are the S3 store types that require a region to be set:
REGIONREQUIRED = ['aws', 'cloudian']

##### NO CHANGES BELOW THIS LINE, PLEASE #####
# these are boolean tags
BOOLTAGS = ['https', 'payload_signing_enabled']
# these are integer tags
INTTAGS = ['port']
# these are the keys that _need_ to have entries in .hs3sh.conf:
REQUIRED = ['endpoint', 'https', 'port',
            'aws_access_key_id', 'aws_secret_access_key']
# these are the keys that are optional:
OPTIONAL = ['comment', 'region', 'signature_version', 'payload_signing_enabled']


class ConfigItems(object):
    'class holding configuration items'

    def __init__(self):
        # from boto3.s3.transfer.TransferConfig():
        self.__mpu_size = 8388608  # multipart_threshold, multipart_chunksize
        self.__mpu_threads = 10    # max_concurrency

        self.__items = []

        for x in self.__dir__():
            if not x.startswith('_'):
                if x not in ['get', 'items']:
                    self.__items.append(x)

    @property
    def items(self):
        return self.__items

    @property
    def get(self):
        _r = []
        for x in self.__dir__():
            if not x.startswith('_'):
                if x not in ['get', 'items']:
                    _r.append('{}: {}'.format(x, getattr(self, x)))

        return _r

    @property
    def get(self):
        _r = []
        for x in self.__dir__():
            if not x.startswith('_'):
                if x == 'mpu_size':
                    _r.append('{}: {} (MB)'
                              .format(x, getattr(self, x)//1024/1024))
                elif x not in ['get', 'items']:
                    _r.append('{}: {}'.format(x, getattr(self, x)))

        return _r

    @property
    def mpu_size(self):
        return int(self.__mpu_size)

    @mpu_size.setter
    def mpu_size(self, value):
        self.__mpu_size = value

    @property
    def mpu_threads(self):
        return int(self.__mpu_threads)

    @mpu_threads.setter
    def mpu_threads(self, value):
        self.__mpu_threads = value

