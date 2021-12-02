'''
# AWS APIGatewayv2 Integrations

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Table of Contents

* [HTTP APIs](#http-apis)

  * [Lambda Integration](#lambda)
  * [HTTP Proxy Integration](#http-proxy)
  * [Private Integration](#private-integration)
  * [Request Parameters](#request-parameters)
* [WebSocket APIs](#websocket-apis)

  * [Lambda WebSocket Integration](#lambda-websocket-integration)

## HTTP APIs

Integrations connect a route to backend resources. HTTP APIs support Lambda proxy, AWS service, and HTTP proxy integrations. HTTP proxy integrations are also known as private integrations.

### Lambda

Lambda integrations enable integrating an HTTP API route with a Lambda function. When a client invokes the route, the
API Gateway service forwards the request to the Lambda function and returns the function's response to the client.

The API Gateway service will invoke the lambda function with an event payload of a specific format. The service expects
the function to respond in a specific format. The details on this format is available at [Working with AWS Lambda
proxy integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html).

The following code configures a route `GET /books` with a Lambda proxy integration.

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import LambdaProxyIntegration

# books_default_fn is of type Function

books_integration = LambdaProxyIntegration(
    handler=books_default_fn
)

http_api = apigwv2.HttpApi(self, "HttpApi")

http_api.add_routes(
    path="/books",
    methods=[apigwv2.HttpMethod.GET],
    integration=books_integration
)
```

### HTTP Proxy

HTTP Proxy integrations enables connecting an HTTP API route to a publicly routable HTTP endpoint. When a client
invokes the route, the API Gateway service forwards the entire request and response between the API Gateway endpoint
and the integrating HTTP endpoint. More information can be found at [Working with HTTP proxy
integrations](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-http.html).

The following code configures a route `GET /books` with an HTTP proxy integration to an HTTP endpoint
`get-books-proxy.myproxy.internal`.

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpProxyIntegration


books_integration = HttpProxyIntegration(
    url="https://get-books-proxy.myproxy.internal"
)

http_api = apigwv2.HttpApi(self, "HttpApi")

http_api.add_routes(
    path="/books",
    methods=[apigwv2.HttpMethod.GET],
    integration=books_integration
)
```

### Private Integration

Private integrations enable integrating an HTTP API route with private resources in a VPC, such as Application Load Balancers or
Amazon ECS container-based applications.  Using private integrations, resources in a VPC can be exposed for access by
clients outside of the VPC.

The following integrations are supported for private resources in a VPC.

#### Application Load Balancer

The following code is a basic application load balancer private integration of HTTP API:

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration


vpc = ec2.Vpc(self, "VPC")
lb = elbv2.ApplicationLoadBalancer(self, "lb", vpc=vpc)
listener = lb.add_listener("listener", port=80)
listener.add_targets("target",
    port=80
)

http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
    default_integration=HttpAlbIntegration(
        listener=listener
    )
)
```

When an imported load balancer is used, the `vpc` option must be specified for `HttpAlbIntegration`.

#### Network Load Balancer

The following code is a basic network load balancer private integration of HTTP API:

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpNlbIntegration


vpc = ec2.Vpc(self, "VPC")
lb = elbv2.NetworkLoadBalancer(self, "lb", vpc=vpc)
listener = lb.add_listener("listener", port=80)
listener.add_targets("target",
    port=80
)

http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
    default_integration=HttpNlbIntegration(
        listener=listener
    )
)
```

When an imported load balancer is used, the `vpc` option must be specified for `HttpNlbIntegration`.

#### Cloud Map Service Discovery

The following code is a basic discovery service private integration of HTTP API:

```python
import aws_cdk.aws_servicediscovery as servicediscovery
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpServiceDiscoveryIntegration


vpc = ec2.Vpc(self, "VPC")
vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
namespace = servicediscovery.PrivateDnsNamespace(self, "Namespace",
    name="boobar.com",
    vpc=vpc
)
service = namespace.create_service("Service")

http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
    default_integration=HttpServiceDiscoveryIntegration(
        vpc_link=vpc_link,
        service=service
    )
)
```

### Request Parameters

Request parameter mapping allows API requests from clients to be modified before they reach backend integrations.
Parameter mapping can be used to specify modifications to request parameters. See [Transforming API requests and
responses](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html).

The following example creates a new header - `header2` - as a copy of `header1` and removes `header1`.

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration

# lb is of type ApplicationLoadBalancer

listener = lb.add_listener("listener", port=80)
listener.add_targets("target",
    port=80
)

http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
    default_integration=HttpAlbIntegration(
        listener=listener,
        parameter_mapping=apigwv2.ParameterMapping().append_header("header2", apigwv2.MappingValue.request_header("header1")).remove_header("header1")
    )
)
```

To add mapping keys and values not yet supported by the CDK, use the `custom()` method:

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration

# lb is of type ApplicationLoadBalancer

listener = lb.add_listener("listener", port=80)
listener.add_targets("target",
    port=80
)

http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
    default_integration=HttpAlbIntegration(
        listener=listener,
        parameter_mapping=apigwv2.ParameterMapping().custom("myKey", "myValue")
    )
)
```

## WebSocket APIs

WebSocket integrations connect a route to backend resources. The following integrations are supported in the CDK.

### Lambda WebSocket Integration

Lambda integrations enable integrating a WebSocket API route with a Lambda function. When a client connects/disconnects
or sends message specific to a route, the API Gateway service forwards the request to the Lambda function

The API Gateway service will invoke the lambda function with an event payload of a specific format.

The following code configures a `sendmessage` route with a Lambda integration

```python
from aws_cdk.aws_apigatewayv2_integrations_alpha import LambdaWebSocketIntegration

# message_handler is of type Function


web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
apigwv2.WebSocketStage(self, "mystage",
    web_socket_api=web_socket_api,
    stage_name="dev",
    auto_deploy=True
)
web_socket_api.add_route("sendmessage",
    integration=LambdaWebSocketIntegration(
        handler=message_handler
    )
)
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

import aws_cdk.aws_apigatewayv2_alpha
import aws_cdk.aws_elasticloadbalancingv2
import aws_cdk.aws_lambda
import aws_cdk.aws_servicediscovery
import constructs


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteIntegration)
class HttpAlbIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpAlbIntegration",
):
    '''(experimental) The Application Load Balancer integration resource for HTTP API.

    :stability: experimental

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration
        
        # lb is of type ApplicationLoadBalancer
        
        listener = lb.add_listener("listener", port=80)
        listener.add_targets("target",
            port=80
        )
        
        http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
            default_integration=HttpAlbIntegration(
                listener=listener,
                parameter_mapping=apigwv2.ParameterMapping().custom("myKey", "myValue")
            )
        )
    '''

    def __init__(
        self,
        *,
        listener: aws_cdk.aws_elasticloadbalancingv2.IApplicationListener,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink] = None,
    ) -> None:
        '''
        :param listener: (experimental) The listener to the application load balancer used for the integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        props = HttpAlbIntegrationProps(
            listener=listener,
            method=method,
            parameter_mapping=parameter_mapping,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig:
        '''(experimental) (experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def _connection_type(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType,
    ) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpMethod:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpMethod, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(self, value: aws_cdk.aws_apigatewayv2_alpha.HttpMethod) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationType")
    def _integration_type(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType,
    ) -> None:
        jsii.set(self, "integrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(
        self,
    ) -> aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion,
    ) -> None:
        jsii.set(self, "payloadFormatVersion", value)


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteIntegration)
class HttpNlbIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpNlbIntegration",
):
    '''(experimental) The Network Load Balancer integration resource for HTTP API.

    :stability: experimental

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpNlbIntegration
        
        
        vpc = ec2.Vpc(self, "VPC")
        lb = elbv2.NetworkLoadBalancer(self, "lb", vpc=vpc)
        listener = lb.add_listener("listener", port=80)
        listener.add_targets("target",
            port=80
        )
        
        http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
            default_integration=HttpNlbIntegration(
                listener=listener
            )
        )
    '''

    def __init__(
        self,
        *,
        listener: aws_cdk.aws_elasticloadbalancingv2.INetworkListener,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink] = None,
    ) -> None:
        '''
        :param listener: (experimental) The listener to the network load balancer used for the integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        props = HttpNlbIntegrationProps(
            listener=listener,
            method=method,
            parameter_mapping=parameter_mapping,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig:
        '''(experimental) (experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def _connection_type(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType,
    ) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpMethod:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpMethod, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(self, value: aws_cdk.aws_apigatewayv2_alpha.HttpMethod) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationType")
    def _integration_type(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType,
    ) -> None:
        jsii.set(self, "integrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(
        self,
    ) -> aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion,
    ) -> None:
        jsii.set(self, "payloadFormatVersion", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpPrivateIntegrationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
    },
)
class HttpPrivateIntegrationOptions:
    def __init__(
        self,
        *,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink] = None,
    ) -> None:
        '''(experimental) Base options for private integration.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_apigatewayv2_alpha as apigatewayv2_alpha
            import aws_cdk.aws_apigatewayv2_integrations_alpha as apigatewayv2_integrations_alpha
            
            # parameter_mapping is of type ParameterMapping
            # vpc_link is of type VpcLink
            
            http_private_integration_options = apigatewayv2_integrations_alpha.HttpPrivateIntegrationOptions(
                method=apigatewayv2_alpha.HttpMethod.ANY,
                parameter_mapping=parameter_mapping,
                secure_server_name="secureServerName",
                vpc_link=vpc_link
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_link(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpPrivateIntegrationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteIntegration)
class HttpProxyIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpProxyIntegration",
):
    '''(experimental) The HTTP Proxy integration resource for HTTP API.

    :stability: experimental

    Example::

        from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpLambdaAuthorizer, HttpLambdaResponseType
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpProxyIntegration
        
        # This function handles your auth logic
        # auth_handler is of type Function
        
        
        authorizer = HttpLambdaAuthorizer(
            authorizer_name="lambda-authorizer",
            response_types=[HttpLambdaResponseType.SIMPLE],  # Define if returns simple and/or iam response
            handler=auth_handler
        )
        
        api = apigwv2.HttpApi(self, "HttpApi")
        
        api.add_routes(
            integration=HttpProxyIntegration(
                url="https://get-books-proxy.myproxy.internal"
            ),
            path="/books",
            authorizer=authorizer
        )
    '''

    def __init__(
        self,
        *,
        url: builtins.str,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
    ) -> None:
        '''
        :param url: (experimental) The full-qualified HTTP URL for the HTTP integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified

        :stability: experimental
        '''
        props = HttpProxyIntegrationProps(
            url=url, method=method, parameter_mapping=parameter_mapping
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig:
        '''(experimental) (experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        _ = aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [_]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpProxyIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "url": "url",
        "method": "method",
        "parameter_mapping": "parameterMapping",
    },
)
class HttpProxyIntegrationProps:
    def __init__(
        self,
        *,
        url: builtins.str,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
    ) -> None:
        '''(experimental) Properties to initialize a new ``HttpProxyIntegration``.

        :param url: (experimental) The full-qualified HTTP URL for the HTTP integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified

        :stability: experimental

        Example::

            from aws_cdk.aws_apigatewayv2_authorizers_alpha import HttpLambdaAuthorizer, HttpLambdaResponseType
            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpProxyIntegration
            
            # This function handles your auth logic
            # auth_handler is of type Function
            
            
            authorizer = HttpLambdaAuthorizer(
                authorizer_name="lambda-authorizer",
                response_types=[HttpLambdaResponseType.SIMPLE],  # Define if returns simple and/or iam response
                handler=auth_handler
            )
            
            api = apigwv2.HttpApi(self, "HttpApi")
            
            api.add_routes(
                integration=HttpProxyIntegration(
                    url="https://get-books-proxy.myproxy.internal"
                ),
                path="/books",
                authorizer=authorizer
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "url": url,
        }
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping

    @builtins.property
    def url(self) -> builtins.str:
        '''(experimental) The full-qualified HTTP URL for the HTTP integration.

        :stability: experimental
        '''
        result = self._values.get("url")
        assert result is not None, "Required property 'url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def method(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpProxyIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteIntegration)
class HttpServiceDiscoveryIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpServiceDiscoveryIntegration",
):
    '''(experimental) The Service Discovery integration resource for HTTP API.

    :stability: experimental

    Example::

        import aws_cdk.aws_servicediscovery as servicediscovery
        from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpServiceDiscoveryIntegration
        
        
        vpc = ec2.Vpc(self, "VPC")
        vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
        namespace = servicediscovery.PrivateDnsNamespace(self, "Namespace",
            name="boobar.com",
            vpc=vpc
        )
        service = namespace.create_service("Service")
        
        http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
            default_integration=HttpServiceDiscoveryIntegration(
                vpc_link=vpc_link,
                service=service
            )
        )
    '''

    def __init__(
        self,
        *,
        service: aws_cdk.aws_servicediscovery.IService,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink] = None,
    ) -> None:
        '''
        :param service: (experimental) The discovery service used for the integration.
        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created

        :stability: experimental
        '''
        props = HttpServiceDiscoveryIntegrationProps(
            service=service,
            method=method,
            parameter_mapping=parameter_mapping,
            secure_server_name=secure_server_name,
            vpc_link=vpc_link,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig:
        '''(experimental) (experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        _ = aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [_]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="connectionType")
    def _connection_type(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType, jsii.get(self, "connectionType"))

    @_connection_type.setter
    def _connection_type(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.HttpConnectionType,
    ) -> None:
        jsii.set(self, "connectionType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="httpMethod")
    def _http_method(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpMethod:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpMethod, jsii.get(self, "httpMethod"))

    @_http_method.setter
    def _http_method(self, value: aws_cdk.aws_apigatewayv2_alpha.HttpMethod) -> None:
        jsii.set(self, "httpMethod", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationType")
    def _integration_type(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType, jsii.get(self, "integrationType"))

    @_integration_type.setter
    def _integration_type(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.HttpIntegrationType,
    ) -> None:
        jsii.set(self, "integrationType", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="payloadFormatVersion")
    def _payload_format_version(
        self,
    ) -> aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion:
        '''
        :stability: experimental
        '''
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion, jsii.get(self, "payloadFormatVersion"))

    @_payload_format_version.setter
    def _payload_format_version(
        self,
        value: aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion,
    ) -> None:
        jsii.set(self, "payloadFormatVersion", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpServiceDiscoveryIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
        "service": "service",
    },
)
class HttpServiceDiscoveryIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink] = None,
        service: aws_cdk.aws_servicediscovery.IService,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpServiceDiscoveryIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created
        :param service: (experimental) The discovery service used for the integration.

        :stability: experimental

        Example::

            import aws_cdk.aws_servicediscovery as servicediscovery
            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpServiceDiscoveryIntegration
            
            
            vpc = ec2.Vpc(self, "VPC")
            vpc_link = apigwv2.VpcLink(self, "VpcLink", vpc=vpc)
            namespace = servicediscovery.PrivateDnsNamespace(self, "Namespace",
                name="boobar.com",
                vpc=vpc
            )
            service = namespace.create_service("Service")
            
            http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
                default_integration=HttpServiceDiscoveryIntegration(
                    vpc_link=vpc_link,
                    service=service
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "service": service,
        }
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_link(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink], result)

    @builtins.property
    def service(self) -> aws_cdk.aws_servicediscovery.IService:
        '''(experimental) The discovery service used for the integration.

        :stability: experimental
        '''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(aws_cdk.aws_servicediscovery.IService, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpServiceDiscoveryIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IHttpRouteIntegration)
class LambdaProxyIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.LambdaProxyIntegration",
):
    '''(experimental) The Lambda Proxy integration resource for HTTP API.

    :stability: experimental

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import LambdaProxyIntegration
        
        # books_default_fn is of type Function
        
        books_integration = LambdaProxyIntegration(
            handler=books_default_fn
        )
        
        http_api = apigwv2.HttpApi(self, "HttpApi")
        
        http_api.add_routes(
            path="/books",
            methods=[apigwv2.HttpMethod.GET],
            integration=books_integration
        )
    '''

    def __init__(
        self,
        *,
        handler: aws_cdk.aws_lambda.IFunction,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        payload_format_version: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion] = None,
    ) -> None:
        '''
        :param handler: (experimental) The handler for this integration.
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param payload_format_version: (experimental) Version of the payload sent to the lambda handler. Default: PayloadFormatVersion.VERSION_2_0

        :stability: experimental
        '''
        props = LambdaProxyIntegrationProps(
            handler=handler,
            parameter_mapping=parameter_mapping,
            payload_format_version=payload_format_version,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IHttpRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig:
        '''(experimental) (experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``HttpRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegrationConfig, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.LambdaProxyIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={
        "handler": "handler",
        "parameter_mapping": "parameterMapping",
        "payload_format_version": "payloadFormatVersion",
    },
)
class LambdaProxyIntegrationProps:
    def __init__(
        self,
        *,
        handler: aws_cdk.aws_lambda.IFunction,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        payload_format_version: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion] = None,
    ) -> None:
        '''(experimental) Lambda Proxy integration properties.

        :param handler: (experimental) The handler for this integration.
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param payload_format_version: (experimental) Version of the payload sent to the lambda handler. Default: PayloadFormatVersion.VERSION_2_0

        :stability: experimental

        Example::

            from aws_cdk.aws_apigatewayv2_integrations_alpha import LambdaProxyIntegration
            
            # books_default_fn is of type Function
            
            books_integration = LambdaProxyIntegration(
                handler=books_default_fn
            )
            
            http_api = apigwv2.HttpApi(self, "HttpApi")
            
            http_api.add_routes(
                path="/books",
                methods=[apigwv2.HttpMethod.GET],
                integration=books_integration
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "handler": handler,
        }
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if payload_format_version is not None:
            self._values["payload_format_version"] = payload_format_version

    @builtins.property
    def handler(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The handler for this integration.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping], result)

    @builtins.property
    def payload_format_version(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion]:
        '''(experimental) Version of the payload sent to the lambda handler.

        :default: PayloadFormatVersion.VERSION_2_0

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
        :stability: experimental
        '''
        result = self._values.get("payload_format_version")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.PayloadFormatVersion], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaProxyIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.aws_apigatewayv2_alpha.IWebSocketRouteIntegration)
class LambdaWebSocketIntegration(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.LambdaWebSocketIntegration",
):
    '''(experimental) Lambda WebSocket Integration.

    :stability: experimental

    Example::

        from aws_cdk.aws_apigatewayv2_integrations_alpha import LambdaWebSocketIntegration
        
        # message_handler is of type Function
        
        
        web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
        apigwv2.WebSocketStage(self, "mystage",
            web_socket_api=web_socket_api,
            stage_name="dev",
            auto_deploy=True
        )
        web_socket_api.add_route("sendmessage",
            integration=LambdaWebSocketIntegration(
                handler=message_handler
            )
        )
    '''

    def __init__(self, *, handler: aws_cdk.aws_lambda.IFunction) -> None:
        '''
        :param handler: (experimental) The handler for this integration.

        :stability: experimental
        '''
        props = LambdaWebSocketIntegrationProps(handler=handler)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="bind")
    def bind(
        self,
        *,
        route: aws_cdk.aws_apigatewayv2_alpha.IWebSocketRoute,
        scope: constructs.Construct,
    ) -> aws_cdk.aws_apigatewayv2_alpha.WebSocketRouteIntegrationConfig:
        '''(experimental) (experimental) Bind this integration to the route.

        :param route: (experimental) The route to which this is being bound.
        :param scope: (experimental) The current scope in which the bind is occurring. If the ``WebSocketRouteIntegration`` being bound creates additional constructs, this will be used as their parent scope.

        :stability: experimental
        '''
        options = aws_cdk.aws_apigatewayv2_alpha.WebSocketRouteIntegrationBindOptions(
            route=route, scope=scope
        )

        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.WebSocketRouteIntegrationConfig, jsii.invoke(self, "bind", [options]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.LambdaWebSocketIntegrationProps",
    jsii_struct_bases=[],
    name_mapping={"handler": "handler"},
)
class LambdaWebSocketIntegrationProps:
    def __init__(self, *, handler: aws_cdk.aws_lambda.IFunction) -> None:
        '''(experimental) Lambda WebSocket Integration props.

        :param handler: (experimental) The handler for this integration.

        :stability: experimental

        Example::

            from aws_cdk.aws_apigatewayv2_integrations_alpha import LambdaWebSocketIntegration
            
            # message_handler is of type Function
            
            
            web_socket_api = apigwv2.WebSocketApi(self, "mywsapi")
            apigwv2.WebSocketStage(self, "mystage",
                web_socket_api=web_socket_api,
                stage_name="dev",
                auto_deploy=True
            )
            web_socket_api.add_route("sendmessage",
                integration=LambdaWebSocketIntegration(
                    handler=message_handler
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "handler": handler,
        }

    @builtins.property
    def handler(self) -> aws_cdk.aws_lambda.IFunction:
        '''(experimental) The handler for this integration.

        :stability: experimental
        '''
        result = self._values.get("handler")
        assert result is not None, "Required property 'handler' is missing"
        return typing.cast(aws_cdk.aws_lambda.IFunction, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LambdaWebSocketIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpAlbIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
        "listener": "listener",
    },
)
class HttpAlbIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink] = None,
        listener: aws_cdk.aws_elasticloadbalancingv2.IApplicationListener,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpAlbIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created
        :param listener: (experimental) The listener to the application load balancer used for the integration.

        :stability: experimental

        Example::

            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpAlbIntegration
            
            # lb is of type ApplicationLoadBalancer
            
            listener = lb.add_listener("listener", port=80)
            listener.add_targets("target",
                port=80
            )
            
            http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
                default_integration=HttpAlbIntegration(
                    listener=listener,
                    parameter_mapping=apigwv2.ParameterMapping().custom("myKey", "myValue")
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "listener": listener,
        }
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_link(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink], result)

    @builtins.property
    def listener(self) -> aws_cdk.aws_elasticloadbalancingv2.IApplicationListener:
        '''(experimental) The listener to the application load balancer used for the integration.

        :stability: experimental
        '''
        result = self._values.get("listener")
        assert result is not None, "Required property 'listener' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.IApplicationListener, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpAlbIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-apigatewayv2-integrations-alpha.HttpNlbIntegrationProps",
    jsii_struct_bases=[HttpPrivateIntegrationOptions],
    name_mapping={
        "method": "method",
        "parameter_mapping": "parameterMapping",
        "secure_server_name": "secureServerName",
        "vpc_link": "vpcLink",
        "listener": "listener",
    },
)
class HttpNlbIntegrationProps(HttpPrivateIntegrationOptions):
    def __init__(
        self,
        *,
        method: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod] = None,
        parameter_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping] = None,
        secure_server_name: typing.Optional[builtins.str] = None,
        vpc_link: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink] = None,
        listener: aws_cdk.aws_elasticloadbalancingv2.INetworkListener,
    ) -> None:
        '''(experimental) Properties to initialize ``HttpNlbIntegration``.

        :param method: (experimental) The HTTP method that must be used to invoke the underlying HTTP proxy. Default: HttpMethod.ANY
        :param parameter_mapping: (experimental) Specifies how to transform HTTP requests before sending them to the backend. Default: undefined requests are sent to the backend unmodified
        :param secure_server_name: (experimental) Specifies the server name to verified by HTTPS when calling the backend integration. Default: undefined private integration traffic will use HTTP protocol
        :param vpc_link: (experimental) The vpc link to be used for the private integration. Default: - a new VpcLink is created
        :param listener: (experimental) The listener to the network load balancer used for the integration.

        :stability: experimental

        Example::

            from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpNlbIntegration
            
            
            vpc = ec2.Vpc(self, "VPC")
            lb = elbv2.NetworkLoadBalancer(self, "lb", vpc=vpc)
            listener = lb.add_listener("listener", port=80)
            listener.add_targets("target",
                port=80
            )
            
            http_endpoint = apigwv2.HttpApi(self, "HttpProxyPrivateApi",
                default_integration=HttpNlbIntegration(
                    listener=listener
                )
            )
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "listener": listener,
        }
        if method is not None:
            self._values["method"] = method
        if parameter_mapping is not None:
            self._values["parameter_mapping"] = parameter_mapping
        if secure_server_name is not None:
            self._values["secure_server_name"] = secure_server_name
        if vpc_link is not None:
            self._values["vpc_link"] = vpc_link

    @builtins.property
    def method(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod]:
        '''(experimental) The HTTP method that must be used to invoke the underlying HTTP proxy.

        :default: HttpMethod.ANY

        :stability: experimental
        '''
        result = self._values.get("method")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpMethod], result)

    @builtins.property
    def parameter_mapping(
        self,
    ) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping]:
        '''(experimental) Specifies how to transform HTTP requests before sending them to the backend.

        :default: undefined requests are sent to the backend unmodified

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-parameter-mapping.html
        :stability: experimental
        '''
        result = self._values.get("parameter_mapping")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.ParameterMapping], result)

    @builtins.property
    def secure_server_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Specifies the server name to verified by HTTPS when calling the backend integration.

        :default: undefined private integration traffic will use HTTP protocol

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-apigatewayv2-integration-tlsconfig.html
        :stability: experimental
        '''
        result = self._values.get("secure_server_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_link(self) -> typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink]:
        '''(experimental) The vpc link to be used for the private integration.

        :default: - a new VpcLink is created

        :stability: experimental
        '''
        result = self._values.get("vpc_link")
        return typing.cast(typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IVpcLink], result)

    @builtins.property
    def listener(self) -> aws_cdk.aws_elasticloadbalancingv2.INetworkListener:
        '''(experimental) The listener to the network load balancer used for the integration.

        :stability: experimental
        '''
        result = self._values.get("listener")
        assert result is not None, "Required property 'listener' is missing"
        return typing.cast(aws_cdk.aws_elasticloadbalancingv2.INetworkListener, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpNlbIntegrationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "HttpAlbIntegration",
    "HttpAlbIntegrationProps",
    "HttpNlbIntegration",
    "HttpNlbIntegrationProps",
    "HttpPrivateIntegrationOptions",
    "HttpProxyIntegration",
    "HttpProxyIntegrationProps",
    "HttpServiceDiscoveryIntegration",
    "HttpServiceDiscoveryIntegrationProps",
    "LambdaProxyIntegration",
    "LambdaProxyIntegrationProps",
    "LambdaWebSocketIntegration",
    "LambdaWebSocketIntegrationProps",
]

publication.publish()
