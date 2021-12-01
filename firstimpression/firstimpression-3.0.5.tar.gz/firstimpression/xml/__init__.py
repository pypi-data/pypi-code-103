import xml.etree.ElementTree as ET


def path_to_root(path: str):
    tree = ET.parse(path)
    return tree.getroot()
