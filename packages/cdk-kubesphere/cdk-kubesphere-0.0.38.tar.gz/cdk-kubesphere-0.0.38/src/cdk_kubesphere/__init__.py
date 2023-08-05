'''
[![NPM version](https://badge.fury.io/js/cdk-kubesphere.svg)](https://badge.fury.io/js/cdk-kubesphere)
[![PyPI version](https://badge.fury.io/py/cdk-kubesphere.svg)](https://badge.fury.io/py/cdk-kubesphere)
![Release](https://github.com/pahud/cdk-kubesphere/workflows/Release/badge.svg)

# cdk-kubesphere

**cdk-kubesphere** is a CDK construct library that allows you to create [KubeSphere](https://kubesphere.io/) on AWS with CDK in TypeScript, JavaScript or Python.

# Sample

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk_kubesphere import KubeSphere

app = cdk.App()

stack = cdk.Stack(app, "cdk-kubesphere-demo")

# deploy a default KubeSphere service on a new Amazon EKS cluster
KubeSphere(stack, "KubeSphere")
```

Behind the scene, the `KubeSphere` construct creates a default Amazon EKS cluster and `KubeSphere` serivce with helm chart([ks-installer](https://github.com/kubesphere/ks-installer)) on it.

<details>
<summary>View helm command</summary>
AWS CDK will helm install the `ks-installer`  on the cluster:

```sh
helm install ks-installer \
--repo https://charts.kubesphere.io/test \
--namespace=kubesphere-system \
--generate-name \
--create-namespace
```

</details>

## KubeSphere App Store

Use `appStore` to enable the [KubeSphere App Store](https://kubesphere.io/docs/pluggable-components/app-store/) support.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
KubeSphere(stack, "KubeSphere",
    app_store=True
)
```

<details>
<summary>View helm command</summary>
AWS CDK will helm install the `ks-installer`  on the cluster:

```sh
helm install ks-installer \
--set openpitrix.enabled=true \
--repo https://charts.kubesphere.io/test \
--namespace=kubesphere-system \
--generate-name \
--create-namespace
```

</details>

# Using existing Amazon EKS clusters

You are allowed to deploy `KubeSphere` in any existing Amazon EKS cluster.

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
cluster = eks.Cluster.from_cluster_attributes(self, "MyCluster",
    cluster_name="my-cluster-name",
    kubectl_role_arn="arn:aws:iam::1111111:role/iam-role-that-has-masters-access"
)

# deploy a default KubeSphere service on the existing Amazon EKS cluster
KubeSphere(stack, "KubeSphere", cluster=cluster)
```

See [Using existing clusters](https://github.com/aws/aws-cdk/tree/master/packages/%40aws-cdk/aws-eks#using-existing-clusters) to learn how to import existing cluster in AWS CDK.

# Console

Run the following command to create a `port-forward` from localhost:8888 to `ks-console:80`

```sh
kubectl -n kubesphere-system port-forward service/ks-console 8888:80
```

Open `http://localhost:8888` and enter the default username/password(`admin/P@88w0rd`) to enter the admin console.
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

import aws_cdk.aws_eks
import aws_cdk.core


class KubeSphere(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-kubesphere.KubeSphere",
):
    '''The KubeSphere workload.'''

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        app_store: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_eks.ICluster] = None,
        nodegroup_options: typing.Optional[aws_cdk.aws_eks.NodegroupOptions] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_store: whether to enable the KubeSphere Application Store(openpitrix). Default: false
        :param cluster: The existing Amazon EKS cluster(if any). Default: - create a default new cluster
        :param nodegroup_options: Options to create the Amazon EKS managed nodegroup. Default: - 2x m5.large on-demand instances
        '''
        props = KubeSphereProps(
            app_store=app_store, cluster=cluster, nodegroup_options=nodegroup_options
        )

        jsii.create(KubeSphere, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-kubesphere.KubeSphereProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_store": "appStore",
        "cluster": "cluster",
        "nodegroup_options": "nodegroupOptions",
    },
)
class KubeSphereProps:
    def __init__(
        self,
        *,
        app_store: typing.Optional[builtins.bool] = None,
        cluster: typing.Optional[aws_cdk.aws_eks.ICluster] = None,
        nodegroup_options: typing.Optional[aws_cdk.aws_eks.NodegroupOptions] = None,
    ) -> None:
        '''The construct properties for KubeSphere.

        :param app_store: whether to enable the KubeSphere Application Store(openpitrix). Default: false
        :param cluster: The existing Amazon EKS cluster(if any). Default: - create a default new cluster
        :param nodegroup_options: Options to create the Amazon EKS managed nodegroup. Default: - 2x m5.large on-demand instances
        '''
        if isinstance(nodegroup_options, dict):
            nodegroup_options = aws_cdk.aws_eks.NodegroupOptions(**nodegroup_options)
        self._values: typing.Dict[str, typing.Any] = {}
        if app_store is not None:
            self._values["app_store"] = app_store
        if cluster is not None:
            self._values["cluster"] = cluster
        if nodegroup_options is not None:
            self._values["nodegroup_options"] = nodegroup_options

    @builtins.property
    def app_store(self) -> typing.Optional[builtins.bool]:
        '''whether to enable the KubeSphere Application Store(openpitrix).

        :default: false
        '''
        result = self._values.get("app_store")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def cluster(self) -> typing.Optional[aws_cdk.aws_eks.ICluster]:
        '''The existing Amazon EKS cluster(if any).

        :default: - create a default new cluster
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.ICluster], result)

    @builtins.property
    def nodegroup_options(self) -> typing.Optional[aws_cdk.aws_eks.NodegroupOptions]:
        '''Options to create the Amazon EKS managed nodegroup.

        :default: - 2x m5.large on-demand instances
        '''
        result = self._values.get("nodegroup_options")
        return typing.cast(typing.Optional[aws_cdk.aws_eks.NodegroupOptions], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KubeSphereProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KubeSphere",
    "KubeSphereProps",
]

publication.publish()
