"""Contains methods to pack sdk api classes to gRPC messages."""
from datetime import datetime
import traceback
from typing import Any, Dict, List, Tuple

from google.protobuf.any_pb2 import Any as GrpcAny
import grpc
from hansken import util
from hansken.util import GeographicLocation

from hansken_extraction_plugin import __version__ as api_version
from hansken_extraction_plugin.api.extraction_plugin import BaseExtractionPlugin, DeferredExtractionPlugin, \
    ExtractionPlugin, MetaExtractionPlugin
from hansken_extraction_plugin.api.plugin_info import Author, PluginInfo, PluginResources
from hansken_extraction_plugin.api.tracelet import Tracelet
from hansken_extraction_plugin.api.transformation import RangedTransformation, Transformation
from hansken_extraction_plugin.framework.DataMessages_pb2 import RpcAuthor, RpcDataStreamTransformation, \
    RpcPluginIdentifier, RpcPluginInfo, RpcPluginResources, RpcPluginType, RpcRange, RpcRangedTransformation, \
    RpcSearchTrace, RpcTrace, RpcTracelet, RpcTraceProperty, RpcTransformation
from hansken_extraction_plugin.framework.PrimitiveMessages_pb2 import RpcBoolean, RpcBytes, RpcDouble, RpcEmptyList, \
    RpcEmptyMap, RpcIsoDateString, RpcLatLong, RpcLong, RpcLongList, RpcMap, RpcString, RpcStringList, RpcStringMap, \
    RpcZonedDateTime
from hansken_extraction_plugin.framework.RpcCallMessages_pb2 import RpcBeginChild, RpcBeginDataStream, RpcEnrichTrace, \
    RpcFinishChild, RpcFinishDataStream, RpcPartialFinishWithError, RpcRead, RpcSearchRequest, RpcWriteDataStream


def any(message: Any) -> GrpcAny:
    """
    Wrap a message in an Any.

    :param message: the message to wrap in an any

    :return: the wrapped message in an Any
    """
    any_request = GrpcAny()
    any_request.Pack(message)
    return any_request


def _list(list):
    if not list:
        return RpcEmptyList()

    if all(type(value) == str for value in list):
        return RpcStringList(values=list)

    if all(type(value) == int for value in list):
        return RpcLongList(values=list)

    raise RuntimeError('currently only homogeneous lists of type str or int are supported')


def _map(map):
    if not map:
        return RpcEmptyMap()

    if all(type(key) == str and type(value) == str for key, value in map.items()):
        msg = RpcStringMap()
        msg.entries.update(map)
        return msg

    rpc_map: Dict[str, Any] = {}
    for key, value in map.items():
        primitive: GrpcAny = any(_primitive(value))
        rpc_map[key] = primitive
    return RpcMap(entries=rpc_map)


def _to_rpc_iso_date_string(dt: datetime) -> RpcIsoDateString:
    return RpcIsoDateString(value=util.format_datetime(dt))


def _to_rpc_zoned_date_time(dt: datetime):
    epoch_second, nano_of_second = _split_aware_datetime(dt)
    zone_offset = dt.strftime('%z')
    zone_id = str(dt.tzinfo)

    return RpcZonedDateTime(epochSecond=epoch_second, nanoOfSecond=nano_of_second,
                            zoneOffset=zone_offset, zoneId=zone_id)


_primitive_matchers = {
    bool: lambda value: RpcBoolean(value=value),
    int: lambda value: RpcLong(value=value),
    float: lambda value: RpcDouble(value=value),
    str: lambda value: RpcString(value=value),
    list: lambda value: _list(value),
    bytes: lambda value: RpcBytes(value=value),
    bytearray: lambda value: RpcBytes(value=bytes(value)),
    datetime: lambda value: _to_rpc_zoned_date_time(value),
    dict: lambda value: _map(value),
    GeographicLocation: lambda value: RpcLatLong(latitude=value[0], longitude=value[1])
}


def _primitive(value: Any):
    valuetype = type(value)
    if valuetype not in _primitive_matchers:
        raise RuntimeError('unable to pack value of type {} '.format(valuetype))

    return _primitive_matchers[valuetype](value)


def _property(name: str, value: Any) -> RpcTraceProperty:
    return RpcTraceProperty(
        name=name,
        value=any(_primitive(value)))


def author(author: Author) -> RpcAuthor:
    """
    Convert given Author to their RpcAuthor counterpart.

    :param author: the author to convert

    :return: the converted author
    """
    return RpcAuthor(
        name=author.name,
        email=author.email,
        organisation=author.organisation)


def _resources(resources: PluginResources) -> RpcPluginResources:
    # NB: Generated protobuf code fails to mark these as optional, while proto3 syntax does state that fields are
    #     optional by default. Types here are ignored to appease mypy only
    # TODO: choose better fix for the optional typing here (HANSKEN-15846)
    return RpcPluginResources(
        maxCpu=resources.maximum_cpu() if resources.maximum_cpu() else None,  # type: ignore
        maxMemory=resources.maximum_memory() if resources.maximum_memory() else None  # type: ignore
    )


def partial_finish_with_error(exception: Exception) -> RpcPartialFinishWithError:
    """
    Convert an exception into the gRPC RpcPartialFinishWithError message.

    :param exception: the exception to convert

    :return: the converted exception
    """
    return RpcPartialFinishWithError(
        actions=[],  # pending actions have not been implemented yet
        statusCode=grpc.StatusCode.CANCELLED.name,
        errorDescription=traceback.format_exc(limit=-1)
    )


def plugin_info(plugin_info: PluginInfo) -> RpcPluginInfo:
    """
    Convert given PluginInfo to their RpcPluginInfo counterpart.

    :param plugin_info: the info to convert

    :return: the converted info
    """
    return RpcPluginInfo(
        type=_plugin_type(plugin_info.plugin),
        # name is deprecated
        version=plugin_info.version,
        apiVersion=api_version,
        description=plugin_info.description,
        author=author(plugin_info.author),
        matcher=plugin_info.matcher,
        webpageUrl=plugin_info.webpage_url,
        maturity=plugin_info.maturity.value,
        deferredIterations=plugin_info.deferred_iterations,
        id=RpcPluginIdentifier(domain=plugin_info.id.domain,
                               category=plugin_info.id.category,
                               name=plugin_info.id.name),
        license=plugin_info.license,
        resources=_resources(plugin_info.resources) if plugin_info.resources else None
    )


def _plugin_type(plugin: BaseExtractionPlugin) -> Any:  # noqa
    if isinstance(plugin, MetaExtractionPlugin):
        return RpcPluginType.MetaExtractionPlugin
    if isinstance(plugin, ExtractionPlugin):
        return RpcPluginType.ExtractionPlugin
    if isinstance(plugin, DeferredExtractionPlugin):
        return RpcPluginType.DeferredExtractionPlugin
    raise RuntimeError(f'unsupported type of plugin: {plugin.__class__.__name__}')


def _properties(properties: Dict[str, Any]):
    return [_property(name, value) for name, value in properties.items()]


def _tracelets(tracelets: List[Tracelet]) -> List[RpcTracelet]:
    return [_tracelet(tracelet) for tracelet in tracelets]


def _tracelet(tracelet: Tracelet) -> RpcTracelet:
    rpc_tracelet_properties = [_property(name, value) for name, value in tracelet.value.items()]
    return RpcTracelet(name=tracelet.name, properties=rpc_tracelet_properties)


def _transformations(transformations: Dict[str, List[Transformation]]) -> List[RpcDataStreamTransformation]:
    return [
        RpcDataStreamTransformation(
            dataType=data_type,
            transformations=[_transformation(transformation) for transformation in transformations]
        )
        for data_type, transformations in transformations.items()
    ]


def _transformation(transformation: Transformation) -> RpcTransformation:
    if isinstance(transformation, RangedTransformation):
        return _ranged_transformation(transformation)
    raise ValueError(f'Unsupported transformation type: {type(transformation).__name__}')


def _ranged_transformation(transformation: RangedTransformation) -> RpcTransformation:
    rpc_ranges: List[RpcRange] = [RpcRange(offset=range.offset, length=range.length) for range in transformation.ranges]
    return RpcTransformation(rangedTransformation=RpcRangedTransformation(ranges=rpc_ranges))


def trace(id: str, types: List[str], properties: Dict[str, Any],
          tracelets: List[Tracelet], transformations: Dict[str, List[Transformation]]) -> RpcTrace:
    """
    Create an RpcTrace from a given set of types and prop.

    :param id: the id of the trace
    :param types: the types of the trace
    :param properties: the properties of the trace
    :param tracelets: the Tracelet properties of the trace, together with the other necessary metadata for a trace.
    :param transformations: the transformations of the trace grouped by data type

    :return: the created message
    """
    return RpcTrace(id=id,
                    types=types,
                    properties=_properties(properties),
                    tracelets=_tracelets(tracelets),
                    transformations=_transformations(transformations))


def _rpc_properties(properties: Dict[str, Any]) -> List[RpcTraceProperty]:
    """
    Convert a dictionary to a list of RpcTraceProperties. This list is useful when serializing an RpcTrace.

    :param properties: dict of properties to convert

    :return: list of RpcTraceProperties
    """
    return [_property(name, value) for name, value in properties.items()]


def search_trace(id: str, properties: Dict[str, Any]) -> RpcSearchTrace:
    """
    Create an RpcSearchTrace from a given id and a set of properties.

    :param id: the id of the trace
    :param properties: the properties of the trace

    :return: the created message
    """
    return RpcSearchTrace(
        id=id,
        properties=_rpc_properties(properties))


def trace_enrichment(trace_id: str, types: List[str], properties: Dict[str, Any],
                     tracelets: List[Tracelet], transformations: Dict[str, List[Transformation]]) -> RpcEnrichTrace:
    """
    Build an RpcEnrichTrace message.

    Create an RpcEnrichTrace message. This message contains a given set of types and
    properties, which is used by the client to enrich the trace being processed.

    :param trace_id: the id of the trace given to it by gRPC
    :param types: the types of the trace
    :param properties: the properties of the trace
    :param tracelets: the Tracelet properties of the trace
    :param transformations: the transformations of the trace

    :return: the created message
    """
    return RpcEnrichTrace(trace=trace(trace_id, types, properties, tracelets, transformations))


def begin_child(trace_id: str, name: str) -> RpcBeginChild:
    """
    Create an RpcBeginChild message.

    The client uses this message to create a new child with provided name and id.

    :param trace_id: the id of the new child trace
    :param name: the name of the new child trace
    """
    return RpcBeginChild(id=trace_id, name=name)


def finish_child(trace_id: str) -> RpcFinishChild:
    """
    Create an RpcFinishChild message.

    When the client received this message, the child with the provided id will be stored.

    :param trace_id: the id of the child trace to store
    """
    return RpcFinishChild(id=trace_id)


def rpc_read(position: int, size: int, trace_uid: str, data_type: str) -> RpcRead:
    """
    Create an RpcRead message.

    :param position: the position to read at
    :param size: the amount of bytes to read
    :param trace_uid: the uid of the trace to read data from
    :param data_type: the type of data to retrieve; raw, html...

    :return: the created message
    """
    return RpcRead(position=position, count=size, traceUid=trace_uid, dataType=data_type)


def rpc_search_request(query: str, count: int) -> RpcSearchRequest:
    """
    Create an RpcSearchRequest from a provided query and count.

    :param query: query to pack
    :param count: count to pack
    :return: packed search request
    """
    return RpcSearchRequest(query=query, count=count)


def rpc_bytes(value: bytes) -> RpcBytes:
    """
    Create an RpcBytes message which contains the supplied byte array.

    :param value: the byte array
    :return: the created message
    """
    return _primitive(value)


def begin_writing(trace_id: str, data_type: str) -> RpcBeginDataStream:
    """
    Create an RpcBeginDataStream message.

    This message is used to indicate that the server will start sending data to write. The client can expect more data
    until an RpcFinishWriting message is sent.

    :param trace_id: id of the trace the data belongs to
    :param data_type: type of the data
    :return: the created message
    """
    return RpcBeginDataStream(traceId=trace_id, dataType=data_type)


def write_data(trace_id: str, data_type: str, data: bytes) -> RpcWriteDataStream:
    """
    Create an RpcWriteDataStream message.

    This message contains data to write for a given trace id and type. Data should be sent sequentially.

    :param trace_id: id of the trace the data belongs to
    :param data_type: type of the data
    :param data: raw bytes to write
    :return: the created message
    """
    return RpcWriteDataStream(traceId=trace_id, dataType=data_type, data=data)


def finish_writing(trace_id: str, data_type: str) -> RpcFinishDataStream:
    """
    Create an RpcFinishDataStream message.

    This message is used to indicate the server has finished writing data to the client. Trying to send more data for
    the same id and type will result in an error.

    :param trace_id: id of the trace the data belongs to
    :param data_type: type of the data
    :return: the created message
    """
    return RpcFinishDataStream(traceId=trace_id, dataType=data_type)


def _split_aware_datetime(dt: datetime) -> Tuple[int, int]:
    """
    Split an aware datetime into seconds & nanoseconds.

    :param dt: an aware datetime instance
    :return: (seconds, nanoseconds)
    """
    if dt.tzinfo is None:
        raise ValueError(f'No timezone set for{dt}')
    return int(dt.timestamp()), dt.microsecond * 1000
