from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..models.http_service_metadata_operations import HttpServiceMetadataOperations
from ..types import UNSET, Unset

T = TypeVar("T", bound="HttpServiceMetadata")


@attr.s(auto_attribs=True)
class HttpServiceMetadata:
    """ """

    api: str
    version: str
    compatibility: str
    languages: Union[Unset, str] = UNSET
    functions: Union[Unset, str] = UNSET
    term_importers: Union[Unset, str] = UNSET
    extensions: Union[Unset, str] = UNSET
    converters: Union[Unset, str] = UNSET
    formatters: Union[Unset, str] = UNSET
    processors: Union[Unset, str] = UNSET
    annotators: Union[Unset, str] = UNSET
    engine: Union[Unset, str] = UNSET
    natures: Union[Unset, str] = UNSET
    trigger: Union[Unset, str] = UNSET
    operations: Union[Unset, HttpServiceMetadataOperations] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        api = self.api
        version = self.version
        compatibility = self.compatibility
        languages = self.languages
        functions = self.functions
        term_importers = self.term_importers
        extensions = self.extensions
        converters = self.converters
        formatters = self.formatters
        processors = self.processors
        annotators = self.annotators
        engine = self.engine
        natures = self.natures
        trigger = self.trigger
        operations: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.operations, Unset):
            operations = self.operations.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "api": api,
                "version": version,
                "compatibility": compatibility,
            }
        )
        if languages is not UNSET:
            field_dict["languages"] = languages
        if functions is not UNSET:
            field_dict["functions"] = functions
        if term_importers is not UNSET:
            field_dict["termImporters"] = term_importers
        if extensions is not UNSET:
            field_dict["extensions"] = extensions
        if converters is not UNSET:
            field_dict["converters"] = converters
        if formatters is not UNSET:
            field_dict["formatters"] = formatters
        if processors is not UNSET:
            field_dict["processors"] = processors
        if annotators is not UNSET:
            field_dict["annotators"] = annotators
        if engine is not UNSET:
            field_dict["engine"] = engine
        if natures is not UNSET:
            field_dict["natures"] = natures
        if trigger is not UNSET:
            field_dict["trigger"] = trigger
        if operations is not UNSET:
            field_dict["operations"] = operations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        api = d.pop("api")

        version = d.pop("version")

        compatibility = d.pop("compatibility")

        languages = d.pop("languages", UNSET)

        functions = d.pop("functions", UNSET)

        term_importers = d.pop("termImporters", UNSET)

        extensions = d.pop("extensions", UNSET)

        converters = d.pop("converters", UNSET)

        formatters = d.pop("formatters", UNSET)

        processors = d.pop("processors", UNSET)

        annotators = d.pop("annotators", UNSET)

        engine = d.pop("engine", UNSET)

        natures = d.pop("natures", UNSET)

        trigger = d.pop("trigger", UNSET)

        _operations = d.pop("operations", UNSET)
        operations: Union[Unset, HttpServiceMetadataOperations]
        if isinstance(_operations, Unset):
            operations = UNSET
        else:
            operations = HttpServiceMetadataOperations.from_dict(_operations)

        http_service_metadata = cls(
            api=api,
            version=version,
            compatibility=compatibility,
            languages=languages,
            functions=functions,
            term_importers=term_importers,
            extensions=extensions,
            converters=converters,
            formatters=formatters,
            processors=processors,
            annotators=annotators,
            engine=engine,
            natures=natures,
            trigger=trigger,
            operations=operations,
        )

        return http_service_metadata
