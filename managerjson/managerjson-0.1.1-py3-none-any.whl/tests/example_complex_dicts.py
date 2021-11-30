_example_1 = {
    "id": "0001",
    "type": "donut",
    "name": "Cake",
    "ppu": 0.55,
    "batters": {
        "batter": [
            {"id": "1001", "type": "Regular"},
            {"id": "1002", "type": "Chocolate"},
            {"id": "1003", "type": "Blueberry"},
            {"id": "1004", "type": "Devil's Food"},
        ]
    },
    "topping": [
        {"id": "5001", "type": "None"},
        {"id": "5002", "type": "Glazed"},
        {"id": "5005", "type": "Sugar"},
        {"id": "5007", "type": "Powdered Sugar"},
        {"id": "5006", "type": "Chocolate with Sprinkles"},
        {"id": "5003", "type": "Chocolate"},
        {"id": "5004", "type": "Maple"},
    ],
}
_example_2 = {
    "id": "0001",
    "type": "donut",
    "name": "Cake",
    "image": {"url": "images/0001.jpg", "width": 200, "height": 200},
    "thumbnail": {"url": "images/thumbnails/0001.jpg", "width": 32, "height": 32},
}
_object_example_1 = {
    "to_objects": {
        "to_object": [
            {
                "id": "0001",
                "type": "donut",
                "name": "Cake",
                "ppu": 0.55,
                "batters": {
                    "batter": [
                        {"id": "1001", "type": "Regular"},
                        {"id": "1002", "type": "Chocolate"},
                        {"id": "1003", "type": "Blueberry"},
                        {"id": "1004", "type": "Devil's Food"},
                    ]
                },
                "topping": [
                    {"id": "5001", "type": "None"},
                    {"id": "5002", "type": "Glazed"},
                    {"id": "5005", "type": "Sugar"},
                    {"id": "5007", "type": "Powdered Sugar"},
                    {"id": "5006", "type": "Chocolate with Sprinkles"},
                    {"id": "5003", "type": "Chocolate"},
                    {"id": "5004", "type": "Maple"},
                ],
            }
        ]
    }
}
_return_flat = {
    "id": "0001",
    "type": "donut",
    "name": "Cake",
    "image_url": "images/0001.jpg",
    "image_width": 200,
    "image_height": 200,
    "thumbnail_url": "images/thumbnails/0001.jpg",
    "thumbnail_width": 32,
    "thumbnail_height": 32,
}


_object_example_2 = {
    "problems": [
        {
            "Diabetes": [
                {
                    "medications": [
                        {
                            "medicationsClasses": [
                                {
                                    "className": [
                                        {
                                            "associatedDrug": [
                                                {
                                                    "name": "asprin",
                                                    "dose": "",
                                                    "strength": "500 mg",
                                                }
                                            ],
                                            "associatedDrug#2": [
                                                {
                                                    "name": "somethingElse",
                                                    "dose": "",
                                                    "strength": "500 mg",
                                                }
                                            ],
                                        }
                                    ],
                                    "className2": [
                                        {
                                            "associatedDrug": [
                                                {
                                                    "name": "asprin",
                                                    "dose": "",
                                                    "strength": "500 mg",
                                                }
                                            ],
                                            "associatedDrug#2": [
                                                {
                                                    "name": "somethingElse",
                                                    "dose": "",
                                                    "strength": "500 mg",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ]
                        }
                    ],
                    "labs": [{"missing_field": "missing_value"}],
                }
            ],
            "Asthma": [{}],
        }
    ]
}
_object_example_3 = {
    "boolean_key": "--- true\n",
    "empty_string_translation": "",
    "key_with_description": "Check it out! This key has a description! (At least in some formats)",
    "key_with_line-break": "This translations contains\na line-break.",
    "nested": {
        "deeply": {"key": "Wow, this key is nested even deeper."},
        "key": "This key is nested inside a namespace.",
    },
    "null_translation": None,
    "pluralized_key": {
        "one": "Only one pluralization found.",
        "other": "Wow, you have %s pluralizations!",
        "zero": "You have no pluralization.",
    },
    "sample_collection": ["first to_object", "second to_object", "third to_object"],
    "simple_key": "Just a simple key with a simple message.",
    "unverified_key": "This translation is not yet verified and waits for it. (In some formats we also export this status)",
}
