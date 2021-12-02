"""RedBrick related helper functions."""


def create_taxonomy_map(taxonomy):
    """
    Create a taxonomy map from RBAI taxonomy object.

    Parameters
    -------------
    taxonomy: Dict
        Redbrick AI taxonomy object:
        [
            {
                "name": str,
                "class_id": int,
                "children": []
            }
            .
            .
        ]

    Returns
    --------------
    taxonomy_map: Dict[int, str]
        maps from class_id to category name
    """
    taxonomy_map = {}
    for category in taxonomy:
        taxonomy_map[category["classId"]] = category["name"]

    return taxonomy_map
