'''
# :superhero_woman: super-eks

**super-eks** is a [CDK]((github.com/aws-cdk/cdk)) construct that provides a preconfigured [EKS](https://aws.amazon.com/eks/) installation with batteries included.
Even when using best practices for your EKS cluster, picking the right setup can be overwhelming.
**super-eks** solves this problem by making a few choices for you as outlined below.

## :sparkles: Features

* :white_check_mark: DNS management with [external-dns](https://github.com/kubernetes-sigs/external-dns)
* :white_check_mark: Forwarding logs to CloudWatch Logs with [fluent-bit](https://github.com/aws/aws-for-fluent-bit)
* :white_check_mark: Ingress management with the [AWS Load Balancer Controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller)
* :white_check_mark: Isolated node groups, one for the shipped components, the other one for your workloads
* :white_check_mark: Hardened node setup, deny nodes altering the VPC setup.
* :white_check_mark: Default to [managed cluster add-ons](https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html#update-cluster-add-ons) where possible.

## :world_map: Roadmap

* :hammer_and_wrench: Monitoring with Prometheus and CloudWatch
* :hammer_and_wrench: Backup solution for cluster recovery
* :hammer_and_wrench: Authentication/authorization for workloads with Amazon Cognito
* :hammer_and_wrench: Standalone one click Cloudformation installer without CDK
* :hammer_and_wrench: Autoscaling for pods and cluster

## :clapper: Quick Start

The quick start shows you how to setup a **super-eks** cluster.

*Prerequisites*

* A working [`aws`](https://aws.amazon.com/cli/) CLI installation with access to an account and administrator privileges
* You'll need a recent [NodeJS](https://nodejs.org) installation
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to interact with your fresh cluster
* An editor of your choice
* Roughly 30 minutes of your time and a :coffee:, :tea: or :beverage_box:

To get going you'll need a CDK project. For details please refer to the [detailed guide for CDK](https://docs.aws.amazon.com/cdk/latest/guide/hello_world.html).

Create an empty directory on your system.

```
mkdir super-eks-setup && cd super-eks-setup
```

Bootstrap your CDK project, we will use TypeScript, but you can switch to any other supported language.

```
npx cdk init sample-app --language typescript
npx cdk bootstrap # Has to be done once for your AWS account
```

Now install the **super-eks** library.

```
npm i @superluminar-io/super-eks
```

You need to provide a Route53 [Hosted zone](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-route53.HostedZone.html) and **super-eks** will take care of the rest.

```
npm i @aws-cdk/aws-route53
```

Paste the snippet into `lib/super-eks-setup-stack.ts`.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
import aws_cdk.core as cdk
from aws_cdk.aws_route53 import HostedZone
from superluminar_io.super_eks import SuperEks

class SuperEksSetupStack(cdk.Stack):
    def __init__(self, scope, id, *, description=None, env=None, stackName=None, tags=None, synthesizer=None, terminationProtection=None, analyticsReporting=None):
        super().__init__(scope, id, description=description, env=env, stackName=stackName, tags=tags, synthesizer=synthesizer, terminationProtection=terminationProtection, analyticsReporting=analyticsReporting)

        # Assumes you already have a Route53 zone in your account
        hosted_zone = HostedZone.from_lookup(self, "MyZone",
            domain_name="example.com"
        )

        # Setup super-eks
        super_eks = SuperEks(self, "hello-eks",
            hosted_zone=hosted_zone
        )

        # Add nginx installation for testing
        super_eks.cluster.add_helm_chart("nginx",
            create_namespace=True,
            namespace="nginx",
            repository="https://charts.bitnami.com/bitnami",
            chart="nginx",
            release="nginx",
            version="8.5.2",
            values={
                "ingress": {
                    "enabled": True,
                    "hostname": f"nginx.{hostedZone.zoneName}",
                    "annotations": {
                        "kubernetes.io/ingress.class": "alb",
                        "alb.ingress.kubernetes.io/scheme": "internet-facing",
                        "alb.ingress.kubernetes.io/target-type": "ip"
                    }
                }
            }
        )
```

Now deploy the stack.

```
npx cdk deploy
```

If everything works, you should see some output.

```
 ✅  IntegrationTestsStack

Outputs:
IntegrationTestsStack.EksClusterConfigCommandAEB22784 = aws eks update-kubeconfig --name EksCluster3394B24C-86f946f02a67416c80413e123d58b628 --region eu-central-1 --role-arn arn:aws:iam::123456789012:role/IntegrationTestsStack-EksClusterMastersRoleA746276-GNW143CGOXG7
IntegrationTestsStack.EksClusterGetTokenCommand53BD6035 = aws eks get-token --cluster-name EksCluster3394B24C-86f946f02a67416c80413e123d58b628 --region eu-central-1 --role-arn arn:aws:iam::123456789012:role/IntegrationTestsStack-EksClusterMastersRoleA746276-GNW143CGOXG7

Stack ARN:
arn:aws:cloudformation:eu-central-1:123456789012:stack/IntegrationTestsStack/06273460-660e-11eb-b4d9-06da4ef2f41a
✨  Done in 1757.52s.
✨  Done in 1757.79s.
```

Paste the `aws eks update-kubeconfig` command into your shell. This will update your `kubeconfig`.

```
aws eks update-kubeconfig --name EksCluster3394B24C-86f946f02a67416c80413e123d58b628 --region eu-central-1 --role-arn arn:aws:iam::123456789012:role/IntegrationTestsStack-EksClusterMastersRoleA746276-GNW143CGOXG7
Added new context arn:aws:eks:eu-central-1:123456789012:cluster/EksCluster3394B24C-86f946f02a67416c80413e123d58b628 to /home/super-eks/.kube/config
```

Now let's see if it works.

```
NAMESPACE      NAME                                            READY   STATUS    RESTARTS   AGE
dns            external-dns-7d4d69545d-r5w68                   1/1     Running   0          14m
logging        aws-for-fluent-bit-qwhwb                        1/1     Running   0          14m
logging        aws-for-fluent-bit-s7wnj                        1/1     Running   0          14m
ingress        aws-load-balancer-controller-5b9cbc5497-smfrt   1/1     Running   0          14m
kube-system    aws-node-lscgc                                  1/1     Running   0          18m
kube-system    aws-node-zfcdl                                  1/1     Running   0          18m
kube-system    coredns-59b69b4849-9gstn                        1/1     Running   0          25m
kube-system    coredns-59b69b4849-bssnr                        1/1     Running   0          25m
kube-system    kube-proxy-9sgtt                                1/1     Running   0          18m
kube-system    kube-proxy-r4gzg                                1/1     Running   0          18m
nginx          nginx-67cb444d48-lqzkg                          1/1     Running   0          14m
```

Voila! :tada: You now have a super EKS cluster with batteries included!

## :open_book: API documentation

See the [API documentation](./API.md) for details.

## :gear: Development

* We use [architecture decision records](https://github.com/joelparkerhenderson/architecture_decision_record/blob/master/adr_template_by_michael_nygard.md). See [here](docs/decisions) for the decisions made so far.
* We use the [AWS Cloud Development Kit (CDK)](github.com/aws-cdk/cdk).
* We use [projen](https://github.com/projen/projen/blob/main/API.md#projen-awscdkconstructlibrary) :heart:. Don't edit package.json etc. Always make changes in [.projenrc.js](./.projenrc.js).

## :question: FAQ

Frequently asked questions are answered here.

### What do you mean by "batteries included"?

[Batteries included](https://www.python.org/dev/peps/pep-0206/#batteries-included-philosophy) is a term that comes from the philosophy behind the Python programming language.
It means, that **super-eks** ships with all necessary parts. You don't need additional things, like in this case Helm charts, manifests etc. apart from the workload you want to run on Kubernetes.

### Why did you choose to include component X?

We try to include components, that are seen as community standards. On the other hand we choose components,
that work best in combination with AWS.

### Where are the advanced settings? I want to do things differently

**super-eks** makes some decisions for you. If you want an expert setup maybe **super-eks** isn't for you.
If you believe core functionality is missing please open a GitHub issue.

### I don't want to use CDK? Do you offer alternatives?

We are planning to release a standalone one click Cloudformation installer in the future.

## :balance_scale: License

**super-eks** is distributed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

See [LICENSE](./LICENSE) for more information.
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_ec2
import aws_cdk.aws_eks
import aws_cdk.aws_iam
import aws_cdk.aws_route53
import aws_cdk.core


@jsii.data_type(
    jsii_type="@superluminar-io/super-eks.AddonProps",
    jsii_struct_bases=[],
    name_mapping={"vpc_cni_addon_version": "vpcCniAddonVersion"},
)
class AddonProps:
    def __init__(
        self,
        *,
        vpc_cni_addon_version: typing.Optional["VpcCniAddonVersion"] = None,
    ) -> None:
        '''Specific properties for EKS managed add-ons.

        :param vpc_cni_addon_version: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if vpc_cni_addon_version is not None:
            self._values["vpc_cni_addon_version"] = vpc_cni_addon_version

    @builtins.property
    def vpc_cni_addon_version(self) -> typing.Optional["VpcCniAddonVersion"]:
        result = self._values.get("vpc_cni_addon_version")
        return typing.cast(typing.Optional["VpcCniAddonVersion"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddonProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@superluminar-io/super-eks.NodeTaint",
    jsii_struct_bases=[],
    name_mapping={"effect": "effect", "key": "key", "value": "value"},
)
class NodeTaint:
    def __init__(
        self,
        *,
        effect: "TaintEffect",
        key: builtins.str,
        value: builtins.str,
    ) -> None:
        '''Represents a Kubernetes taint.

        See `https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ <https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/>`_

        :param effect: 
        :param key: 
        :param value: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "effect": effect,
            "key": key,
            "value": value,
        }

    @builtins.property
    def effect(self) -> "TaintEffect":
        result = self._values.get("effect")
        assert result is not None, "Required property 'effect' is missing"
        return typing.cast("TaintEffect", result)

    @builtins.property
    def key(self) -> builtins.str:
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NodeTaint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SuperEks(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@superluminar-io/super-eks.SuperEks",
):
    '''SuperEks wraps eks.Cluster to include batteries.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        hosted_zone: aws_cdk.aws_route53.IHostedZone,
        addon_props: typing.Optional[AddonProps] = None,
        admin_roles: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IRole]] = None,
        cluster_props: typing.Optional[aws_cdk.aws_eks.ClusterProps] = None,
        super_eks_nodegroup_props: typing.Optional[aws_cdk.aws_eks.NodegroupOptions] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: A hosted zone for DNS management. Records in this zone will be created for your workloads by 'external-dns'.
        :param addon_props: Specific properties for EKS managed add-ons.
        :param admin_roles: Additional Roles that should be granted cluster admin privileges. Can also be added manually after cluster creation by using ``cluster.awsAuth.addMastersRole(role)``.
        :param cluster_props: Wrapper for all cluster props>.
        :param super_eks_nodegroup_props: Config for the Nodegroup created to host SuperEks specific workloads. If you override the ``launchTemplateSpec`` you're responsible for adding the necessary userdata to taint the nodes, see ``../config/cluster#nodeTaintUserdata``
        '''
        props = SuperEksProps(
            hosted_zone=hosted_zone,
            addon_props=addon_props,
            admin_roles=admin_roles,
            cluster_props=cluster_props,
            super_eks_nodegroup_props=super_eks_nodegroup_props,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="nodeTaintUserdata")
    def node_taint_userdata(
        self,
        *,
        effect: "TaintEffect",
        key: builtins.str,
        value: builtins.str,
    ) -> aws_cdk.aws_ec2.MultipartUserData:
        '''Generates ``ec2.MultipartUserData`` to attach to a ``eks.Nodegroup`` ``ec2.LaunchTemplate`` so that the Nodes are getting tainted with the given ``NodeTaint``.

        :param effect: 
        :param key: 
        :param value: 
        '''
        taint = NodeTaint(effect=effect, key=key, value=value)

        return typing.cast(aws_cdk.aws_ec2.MultipartUserData, jsii.invoke(self, "nodeTaintUserdata", [taint]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="additionalNodegroups")
    def additional_nodegroups(self) -> typing.List[aws_cdk.aws_eks.Nodegroup]:
        '''``eks.Nodegroup``s added to the cluster.

        :default: An internal ``eks.Nodegroup`` will be created for super-eks related workloads

        :attribute: true
        '''
        return typing.cast(typing.List[aws_cdk.aws_eks.Nodegroup], jsii.get(self, "additionalNodegroups"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cluster")
    def cluster(self) -> aws_cdk.aws_eks.Cluster:
        '''The created cluster.

        :attribute: true
        '''
        return typing.cast(aws_cdk.aws_eks.Cluster, jsii.get(self, "cluster"))


@jsii.data_type(
    jsii_type="@superluminar-io/super-eks.SuperEksProps",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "addon_props": "addonProps",
        "admin_roles": "adminRoles",
        "cluster_props": "clusterProps",
        "super_eks_nodegroup_props": "superEksNodegroupProps",
    },
)
class SuperEksProps:
    def __init__(
        self,
        *,
        hosted_zone: aws_cdk.aws_route53.IHostedZone,
        addon_props: typing.Optional[AddonProps] = None,
        admin_roles: typing.Optional[typing.Sequence[aws_cdk.aws_iam.IRole]] = None,
        cluster_props: typing.Optional[aws_cdk.aws_eks.ClusterProps] = None,
        super_eks_nodegroup_props: typing.Optional[aws_cdk.aws_eks.NodegroupOptions] = None,
    ) -> None:
        '''Constructor properties for SuperEks.

        Get merged with ``defaultSuperEksProps``.

        :param hosted_zone: A hosted zone for DNS management. Records in this zone will be created for your workloads by 'external-dns'.
        :param addon_props: Specific properties for EKS managed add-ons.
        :param admin_roles: Additional Roles that should be granted cluster admin privileges. Can also be added manually after cluster creation by using ``cluster.awsAuth.addMastersRole(role)``.
        :param cluster_props: Wrapper for all cluster props>.
        :param super_eks_nodegroup_props: Config for the Nodegroup created to host SuperEks specific workloads. If you override the ``launchTemplateSpec`` you're responsible for adding the necessary userdata to taint the nodes, see ``../config/cluster#nodeTaintUserdata``
        '''
        if isinstance(addon_props, dict):
            addon_props = AddonProps(**addon_props)
        if isinstance(cluster_props, dict):
            cluster_props = aws_cdk.aws_eks.ClusterProps(**cluster_props)
        if isinstance(super_eks_nodegroup_props, dict):
            super_eks_nodegroup_props = aws_cdk.aws_eks.NodegroupOptions(**super_eks_nodegroup_props)
        self._values: typing.Dict[str, typing.Any] = {
            "hosted_zone": hosted_zone,
        }
        if addon_props is not None:
            self._values["addon_props"] = addon_props
        if admin_roles is not None:
            self._values["admin_roles"] = admin_roles
        if cluster_props is not None:
            self._values["cluster_props"] = cluster_props
        if super_eks_nodegroup_props is not None:
            self._values["super_eks_nodegroup_props"] = super_eks_nodegroup_props

    @builtins.property
    def hosted_zone(self) -> aws_cdk.aws_route53.IHostedZone:
        '''A hosted zone for DNS management.

        Records in this zone will be created for your workloads by 'external-dns'.
        '''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(aws_cdk.aws_route53.IHostedZone, result)

    @builtins.property
    def addon_props(self) -> typing.Optional[AddonProps]:
        '''Specific properties for EKS managed add-ons.'''
        result = self._values.get("addon_props")
        return typing.cast(typing.Optional[AddonProps], result)

    @builtins.property
    def admin_roles(self) -> typing.Optional[typing.List[aws_cdk.aws_iam.IRole]]:
        '''Additional Roles that should be granted cluster admin privileges.

        Can also be added manually after cluster creation by using ``cluster.awsAuth.addMastersRole(role)``.
        '''
        result = self._values.get("admin_roles")
        return typing.cast(typing.Optional[typing.List[aws_cdk.aws_iam.IRole]], result)

    @builtins.property
    def cluster_props(self) -> typing.Optional[aws_cdk.aws_eks.ClusterProps]:
        '''Wrapper for all cluster props>.'''
        result = self._values.get("cluster_props")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.ClusterProps], result)

    @builtins.property
    def super_eks_nodegroup_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_eks.NodegroupOptions]:
        '''Config for the Nodegroup created to host SuperEks specific workloads.

        If you override the ``launchTemplateSpec`` you're responsible for adding the necessary userdata to taint the nodes,
        see ``../config/cluster#nodeTaintUserdata``
        '''
        result = self._values.get("super_eks_nodegroup_props")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.NodegroupOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SuperEksProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@superluminar-io/super-eks.TaintEffect")
class TaintEffect(enum.Enum):
    '''Represents a Kubernetes taint effect.

    See `https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/ <https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/>`_
    '''

    NO_SCHEDULE = "NO_SCHEDULE"
    PREFER_NO_SCHEDULE = "PREFER_NO_SCHEDULE"
    NO_EXECUTE = "NO_EXECUTE"


class VpcCniAddonVersion(
    metaclass=jsii.JSIIMeta,
    jsii_type="@superluminar-io/super-eks.VpcCniAddonVersion",
):
    '''vpc-cni add-on versions.'''

    def __init__(self, version: builtins.str) -> None:
        '''
        :param version: add-on version.
        '''
        jsii.create(self.__class__, self, [version])

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, version: builtins.str) -> "VpcCniAddonVersion":
        '''Custom add-on version.

        :param version: custom add-on version.
        '''
        return typing.cast("VpcCniAddonVersion", jsii.sinvoke(cls, "of", [version]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_6_3")
    def V1_6_3(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.6.3.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_6_3"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_7_5")
    def V1_7_5(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.7.5.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_7_5"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_7_6")
    def V1_7_6(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.7.6.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_7_6"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="V1_7_9")
    def V1_7_9(cls) -> "VpcCniAddonVersion":
        '''vpc-cni version 1.7.9.'''
        return typing.cast("VpcCniAddonVersion", jsii.sget(cls, "V1_7_9"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        '''add-on version.'''
        return typing.cast(builtins.str, jsii.get(self, "version"))


__all__ = [
    "AddonProps",
    "NodeTaint",
    "SuperEks",
    "SuperEksProps",
    "TaintEffect",
    "VpcCniAddonVersion",
]

publication.publish()
