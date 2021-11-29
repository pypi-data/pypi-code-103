class Service:
    def __init__(self, client, arn):
        self.client = client
        self.arn = self._long_arn(arn)
        self.name = arn.split("/")[-1]

    @property
    def hostname(self):
        hostname = f"{self.name}.{self.client.namespace}"
        return hostname

    @property
    def tags(self):
        if not self.service_discovery_arn:
            return {}

        tags = self.client.service_discovery.list_tags_for_resource(
            ResourceARN=self.service_discovery_arn
        ).get("Tags")
        return dict([(tag["Key"], tag["Value"]) for tag in tags])

    @property
    def service_discovery_arn(self):
        service = self.client.ecs.describe_services(
            cluster=self.client.cluster_name,
            services=[self.arn],
        ).get("services", [{}])[0]

        registries = service.get("serviceRegistries") or [{}]
        arn = registries[0].get("registryArn")

        return arn

    def _long_arn(self, arn):
        # https://docs.aws.amazon.com/AmazonECS/latest/userguide/ecs-account-settings.html#ecs-resource-ids
        arn_parts = arn.split("/")
        if len(arn_parts) == 3:
            # A new long arn:
            # arn:aws:ecs:region:aws_account_id:service/cluster-name/service-name
            # Return it as is
            return arn
        else:
            # An old short arn:
            # arn:aws:ecs:region:aws_account_id:service/service-name
            # Add the cluster name
            return "/".join([arn_parts[0], self.client.cluster_name, arn_parts[1]])
