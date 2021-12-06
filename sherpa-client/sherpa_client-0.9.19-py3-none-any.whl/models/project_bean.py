from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..models.classification_config import ClassificationConfig
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectBean")


@attr.s(auto_attribs=True)
class ProjectBean:
    """ """

    name: str
    label: str
    image: str
    lang: str
    description: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    documents: Union[Unset, int] = UNSET
    segments: Union[Unset, int] = UNSET
    annotations: Union[Unset, int] = UNSET
    categories: Union[Unset, int] = UNSET
    nature: Union[Unset, str] = UNSET
    created_by: Union[Unset, str] = UNSET
    created_date: Union[Unset, str] = UNSET
    owner: Union[Unset, str] = UNSET
    group_name: Union[Unset, str] = UNSET
    shared: Union[Unset, bool] = UNSET
    read_only: Union[Unset, bool] = UNSET
    private: Union[Unset, bool] = UNSET
    engines: Union[Unset, List[str]] = UNSET
    algorithms: Union[Unset, List[str]] = UNSET
    metafacets: Union[Unset, List[Any]] = UNSET
    classification: Union[Unset, ClassificationConfig] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        label = self.label
        description = self.description
        image = self.image
        lang = self.lang
        version = self.version
        documents = self.documents
        segments = self.segments
        annotations = self.annotations
        categories = self.categories
        nature = self.nature
        created_by = self.created_by
        created_date = self.created_date
        owner = self.owner
        group_name = self.group_name
        shared = self.shared
        read_only = self.read_only
        private = self.private
        engines: Union[Unset, List[str]] = UNSET
        if not isinstance(self.engines, Unset):
            engines = self.engines

        algorithms: Union[Unset, List[str]] = UNSET
        if not isinstance(self.algorithms, Unset):
            algorithms = self.algorithms

        metafacets: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.metafacets, Unset):
            metafacets = []
            for metafacets_item_data in self.metafacets:
                metafacets_item = metafacets_item_data

                metafacets.append(metafacets_item)

        classification: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.classification, Unset):
            classification = self.classification.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "label": label,
                "image": image,
                "lang": lang,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if version is not UNSET:
            field_dict["version"] = version
        if documents is not UNSET:
            field_dict["documents"] = documents
        if segments is not UNSET:
            field_dict["segments"] = segments
        if annotations is not UNSET:
            field_dict["annotations"] = annotations
        if categories is not UNSET:
            field_dict["categories"] = categories
        if nature is not UNSET:
            field_dict["nature"] = nature
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if created_date is not UNSET:
            field_dict["createdDate"] = created_date
        if owner is not UNSET:
            field_dict["owner"] = owner
        if group_name is not UNSET:
            field_dict["groupName"] = group_name
        if shared is not UNSET:
            field_dict["shared"] = shared
        if read_only is not UNSET:
            field_dict["readOnly"] = read_only
        if private is not UNSET:
            field_dict["private"] = private
        if engines is not UNSET:
            field_dict["engines"] = engines
        if algorithms is not UNSET:
            field_dict["algorithms"] = algorithms
        if metafacets is not UNSET:
            field_dict["metafacets"] = metafacets
        if classification is not UNSET:
            field_dict["classification"] = classification

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        label = d.pop("label")

        image = d.pop("image")

        lang = d.pop("lang")

        description = d.pop("description", UNSET)

        version = d.pop("version", UNSET)

        documents = d.pop("documents", UNSET)

        segments = d.pop("segments", UNSET)

        annotations = d.pop("annotations", UNSET)

        categories = d.pop("categories", UNSET)

        nature = d.pop("nature", UNSET)

        created_by = d.pop("createdBy", UNSET)

        created_date = d.pop("createdDate", UNSET)

        owner = d.pop("owner", UNSET)

        group_name = d.pop("groupName", UNSET)

        shared = d.pop("shared", UNSET)

        read_only = d.pop("readOnly", UNSET)

        private = d.pop("private", UNSET)

        engines = cast(List[str], d.pop("engines", UNSET))

        algorithms = cast(List[str], d.pop("algorithms", UNSET))

        metafacets = []
        _metafacets = d.pop("metafacets", UNSET)
        for metafacets_item_data in _metafacets or []:
            metafacets_item = metafacets_item_data

            metafacets.append(metafacets_item)

        _classification = d.pop("classification", UNSET)
        classification: Union[Unset, ClassificationConfig]
        if isinstance(_classification, Unset):
            classification = UNSET
        else:
            classification = ClassificationConfig.from_dict(_classification)

        project_bean = cls(
            name=name,
            label=label,
            description=description,
            image=image,
            lang=lang,
            version=version,
            documents=documents,
            segments=segments,
            annotations=annotations,
            categories=categories,
            nature=nature,
            created_by=created_by,
            created_date=created_date,
            owner=owner,
            group_name=group_name,
            shared=shared,
            read_only=read_only,
            private=private,
            engines=engines,
            algorithms=algorithms,
            metafacets=metafacets,
            classification=classification,
        )

        return project_bean
