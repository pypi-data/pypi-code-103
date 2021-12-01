{
    "ébauches": {
        "required": True,
        "type": "dict",
        "empty": False,
        "valuesrules": {"type": "string", "nullable": True},
    },
    "tests": {
        "required": True,
        "type": "list",
        "empty": False,
        "schema": {
            "required": True,
            "type": "dict",
            "schema": {
                "nom": {"required": False, "type": "string"},
                "entrée": {
                    "required": False,
                    "type": ["string", "integer"],
                    "nullable": True,
                },
                "sortie": {
                    "required": True,
                    "type": ["string", "integer"],
                    "nullable": True,
                },
                "rétroactions": {
                    "required": False,
                    "type": "dict",
                    "schema": "rétroactions",
                },
            },
        },
    },
}
