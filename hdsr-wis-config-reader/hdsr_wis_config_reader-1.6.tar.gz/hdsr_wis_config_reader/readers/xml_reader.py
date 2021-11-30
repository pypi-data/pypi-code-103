from collections import defaultdict
from lxml import etree as ET
from pathlib import Path
from typing import Dict
from typing import Union


class XmlReader:
    @classmethod
    def __xml_to_etree(cls, xml_filepath: Path) -> ET._Element:
        """Parses an xml-file to an etree. ETree can be used in function etree_to_dict"""
        assert isinstance(xml_filepath, Path), f"path {xml_filepath} must be a pathlib.Path"
        etree = ET.parse(source=xml_filepath.as_posix()).getroot()
        return etree

    @classmethod
    def __etree_to_dict(
        cls, etree: Union[ET._Element, ET._Comment], section_start: str = None, section_end: str = None,
    ) -> Dict:
        """converts an etree to a dictionary"""
        assert isinstance(etree, ET._Comment) or isinstance(
            etree, ET._Element
        ), f"etree {etree} must be either be a ET._Comment or ET._Element"
        if isinstance(etree, ET._Comment):
            return {}
        _dict = {etree.tag.rpartition("}")[-1]: {} if etree.attrib else None}
        children = list(etree)

        # get a section only
        if section_start or section_end:
            if section_start:
                start = [
                    idx
                    for idx, child in enumerate(children)
                    if isinstance(child, ET._Comment)
                    if ET.tostring(child).decode("utf-8").strip() == section_start
                ][0]
            else:
                start = 0
            if section_end:
                end = [
                    idx
                    for idx, child in enumerate(children)
                    if isinstance(child, ET._Comment)
                    if ET.tostring(child).decode("utf-8").strip() == section_end
                ][0]
                if start < end:
                    children = children[start:end]
            else:
                children = children[start:]

        children = [child for child in children if not isinstance(child, ET._Comment)]

        if children:
            dd = defaultdict(list)
            # for dc in map(etree_to_dict, children):
            for dc in [cls.__etree_to_dict(etree=child) for child in children]:
                for k, v in dc.items():
                    dd[k].append(v)

            _dict = {etree.tag.rpartition("}")[-1]: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if etree.attrib:
            _dict[etree.tag.rpartition("}")[-1]].update((k, v) for k, v in etree.attrib.items())
        if etree.text:
            text = etree.text.strip()
            if children or etree.attrib:
                if text:
                    _dict[etree.tag.rpartition("}")[-1]]["#text"] = text
            else:
                _dict[etree.tag.rpartition("}")[-1]] = text
        return _dict

    @classmethod
    def xml_to_dict(cls, xml_filepath: Path, section_start: str = None, section_end: str = None) -> Dict:
        """Convert an xml-file to a dictionary"""
        etree = cls.__xml_to_etree(xml_filepath=xml_filepath)
        _dict = cls.__etree_to_dict(etree=etree, section_start=section_start, section_end=section_end)
        return _dict
