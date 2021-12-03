from boto3.session import Session
from os import system

# config = load_config('config.yml')

# _aws_session = Session(
#     region_name='eu-central-1',
#     aws_access_key_id=config['aws_access_key_id'],
#     aws_secret_access_key=config['aws_access_key_id']
# )


class S3():

    def __init__(self, aws_id,  aws_sec_key):
        self.aws_id = aws_id
        self.secret_key = aws_sec_key
        
        self._aws_session = Session(
            region_name='eu-central-1',
            aws_access_key_id=self.aws_id,
            aws_secret_access_key=self.secret_key
        )
        print(self.aws_id , self.secret_key)        
        # self._login()

    def _login(self):
        system(f'''export AWS_ACCESS_KEY_ID={self.aws_id} &&
            export AWS_SECRET_ACCESS_KEY={self.secret_key}
            eval $(aws ecr get-login --no-include-email --region eu-central-1)''')

    def get_secure_url(self, bucket, filename, expires_in=7200, insecure=False):
                
        # max is 7 days
        if not expires_in:
            expires_in = 7200
        elif expires_in > 604800:
            expires_in = 604800
        
        url = self._aws_session.client('s3').generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket, 'Key': filename},
            ExpiresIn=expires_in
        )
        
        if insecure:
            return url.split("?")[0]
        else:
            return url
