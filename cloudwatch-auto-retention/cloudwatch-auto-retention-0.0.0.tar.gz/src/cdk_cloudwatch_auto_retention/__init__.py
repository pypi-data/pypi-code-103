'''
# cdk-cloudwatch-logs-auto-retention

cdk-cloudwatch-logs-auto-retention is an AWS CDK construct library that will check once a month if you have any Cloudwatch Log Groups in the region it is deployed with a never-expire retention and auto-fix this to one month. This is a cost-optimization as Cloudwatch Logs have a very high storage cost. If you need Cloudwatch logs for longer you should set an automated S3 export (cdk-cloudwatch-logs-s3-export is in the works 😚).

## Getting started

### TypeScript

#### Installation

//TODO

#### Usage

```python
# Example automatically generated from non-compiling source. May contain errors.
```
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

import aws_cdk.core


class CdkCloudwatchAutoRetention(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudwatch-auto-retention.CdkCloudwatchAutoRetention",
):
    def __init__(self, scope: aws_cdk.core.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(self.__class__, self, [scope, id])


__all__ = [
    "CdkCloudwatchAutoRetention",
]

publication.publish()
