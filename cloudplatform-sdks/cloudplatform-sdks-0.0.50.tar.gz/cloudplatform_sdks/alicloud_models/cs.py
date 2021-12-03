from .clients import cs_client


class AliCs:
    """
    {"clusters" : [ {
     "cluster_id" : "c3fb96524f9274b4495df0f12a6b5****",
     "cluster_type" : "Kubernetes",
     "created" : "2020-08-20T10:51:29+08:00",
     "init_version" : "1.16.9-aliyun.1",
     "current_version" : "1.16.9-aliyun.1",
     "next_version" : "1.18.8-aliyun.1",
     "deletion_protection" : true,
     "docker_version" : "19.03.5",
     "external_loadbalancer_id" : "lb-2vcrbmlevo6kjpgch****",
     "master_url" : "{
                \\\"api_server_endpoint\\\":\\\"\\\",
            \\\"intranet_api_server_endpoint\\\":\\\"https://192.1 68.0.251:6443\\\"}",
            "meta_data" : "{
                \\\"Addons\\\":[{
                    \\\"config\\\":***}",
                    "name" : "cluster-demo",
                    "network_mode" : "vpc",
                    "private_zone" : false,
                    "profile" : "Default",
                    "region_id" : "cn-beijing",
                    "resource_group_id" : "rg-acfmyvw3wjm****",
                     "security_group_id" : "sg-2vcgwsrwgt5mp0yi****",
                     "size" : 5,
                     "state" : "running",
                      "subnet_cidr" : "172.21.0.0/16",
                      "tags" : [ { "key" : "env", "value" : "prod" } ],
                      "updated" : "2020-09-16T11:09:55+08:00",
                      "vpc_id" : "vpc-2vcg932hsxsxuqbgl****",
                       "vswitch_id" : "vsw-2vc41xuumx5z2rdma****,vsw-2vc41xuumx5z2rdma****",
                        "worker_ram_role_name" : "KubernetesWorkerRole-ec87d15b-edca-4302-933f-c8a16bf0****",
                         "zone_id" : "cn-beijing-b", } ],
                          "page_info" : { "page_number" : 3, "page_size" : 20, "total_count" : 50 }}
    """

    def __init__(self, cs_info):
        self.cs_info = cs_info

    @classmethod
    def get_k8s_list(cls, params=None):
        max_len = 50
        if isinstance(params, dict):
            params['PageSize'] = params.get('PageSize', max_len)
        else:
            params = {'PageSize': max_len}
        return cs_client.describe_clusters(params)

    @classmethod
    def get_k8s_detail(cls, params=None):
        return cs_client.describe_detail_clusters(params)
