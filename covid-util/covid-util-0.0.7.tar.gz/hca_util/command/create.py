import json

from botocore.config import Config
from botocore.exceptions import ClientError
from hca_util.bucket_policy import new_policy_statement
from hca_util.common import gen_uuid
from hca_util.common import print_err


class CmdCreate:
    """
    user: wrangler only
    aws resource or client used in command - s3 client (put_object), s3 resource (BucketPolicy)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        if self.aws.is_contributor:
            return False, 'You don\'t have permission to use this command'

        area_name = self.args.NAME
        perms = self.args.p  # optional str, default 'ux'

        # generate random uuid prefix for area name
        area_id = gen_uuid()

        try:
            metadata = {'name': area_name, 'perms': perms}

            s3_client = self.aws.common_session.client('s3', endpoint_url='https://uk1s3.embassy.ebi.ac.uk', config=Config(s3={'addressing_style': 'path'}))
            s3_client.put_object(Bucket=self.aws.bucket_name, Key=(area_id + '/'), Metadata=metadata)

            return True, 'Created upload area with UUID ' + area_id + ' and name ' + area_name

        except Exception as e:
            print_err(e, 'create')
