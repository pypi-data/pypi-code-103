from .client import HuaweiClient
from huaweicloudsdkiam.v3 import IamClient
from huaweicloudsdkiam.v3.region.iam_region import IamRegion


class HuaweiIamClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiIamClient, self).__init__(*args, **kwargs)

    @property
    def iam_client(self):
        return self.generate_global_client(IamClient, IamRegion)

    def regions(self, request):
        if self.region:
            client = IamClient.new_builder(). \
                with_credentials(self.global_credentials). \
                with_region(IamRegion.value_of(self.region)). \
                build()
            return client.keystone_list_regions(request).regions
        else:
            # huawei query region API required params `region`, ergodic all huawei's regions until find a available one
            region_lst = ['cn-east-2', 'cn-east-201', 'cn-east-3', 'cn-north-1', 'cn-north-219', 'cn-north-4',
                          'cn-north-9', 'cn-northeast-1', 'cn-south-1', 'cn-south-4', 'cn-southwest-2', 'la-north-2',
                          'la-south-2', 'na-mexico-1', 'sa-brazil-1', 'af-south-1', 'ap-southeast-1', 'ap-southeast-2',
                          'ap-southeast-3']

            for region in region_lst:
                try:
                    self.region = region
                    client = IamClient.new_builder(). \
                        with_credentials(self.global_credentials). \
                        with_region(IamRegion.value_of(self.region)). \
                        build()
                    return client.keystone_list_regions(request).regions
                except Exception:
                    continue
            raise Exception("AK/SK validate failed, please check avaliable region")

