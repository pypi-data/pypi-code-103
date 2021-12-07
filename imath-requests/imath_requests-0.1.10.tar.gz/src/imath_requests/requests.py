# Request handelling and data structures for interacting with iMath REST API

class PartData:
    def __init__(self, timestamp, part_id, source, part_data):
        self.timestamp = timestamp # Timestamp e.g. 1516193959559
        self.part_id = part_id # Unique part ID e.g. Part1234
        self.source = source # Data source e.g. I3DR_DESKTOP_ABC123
        # Part data should be a key value pair array e.g.
        # part_data = [
        # 	{
        # 		"key": "steel_grade",
        # 		"value": "Grade01"
        # 	},
        # 	{
        # 		"key": "analysis",
        # 		"value": [
        # 			{
        # 				"key": "C",
        # 				"value": "0.2"
        # 			},
        # 			{
        # 				"key": "Mn",
        # 				"value": "0.02"
        # 			}
        # 		]
        # 	}
        # ]
        self.part_data = part_data

    def get_json(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "part_id": self.part_id,
            "source": self.source,
            "part_data": self.part_data
        }


class ImageValue:
    def __init__(self, value, timestamp, position, dimension, quality):
        self.value = value # name of the image
        self.timestamp = timestamp # Timestamp e.g. 1516193959559
        # position on the part where the image was taken
        self.position = position
        self.dimension = dimension # dimension of the area of the part, which is on the image
        self.quality = quality

    def get_json(self) -> dict:
        return {
            "value": self.value,
            "timestamp": self.timestamp,
            "position": self.position,
            "dimension": self.dimension,
            "quality": self.quality
        }


class ImageMetaData:
    def __init__(self, part_id, value_id, source, values: list, qualifying_metadata):
        self.part_id = part_id # Unique part ID e.g. Part1234
        self.value_id = value_id # Unique identification of the capture device e.g. Camera1
        self.source = source # Data source e.g. I3DR_DESKTOP_ABC123
        # Values should be a list of ImageValues
        self.values = []
        for value in values:
            self.values.append(value.get_json())
        # Qualifying metadata should be a key value pair array e.g.
        # qualifying_metadata = [
        # 	{
        # 		"key": "key1",
        # 		"value": "value1"
        # 	},
        # 	{
        # 		"key": "key2",
        # 		"value": "value2"
        # 	}
        # ]
        self.qualifying_metadata = qualifying_metadata

    def get_json(self) -> dict:
        return {
            "part_id": self.part_id,
            "value_id": self.value_id,
            "source": self.source,
            "values": self.values,
            "qualifying_metadata": self.qualifying_metadata
        }


class ImageAnalysisData:
    def __init__(self, part_id, source, value, timestamp):
        raise NotImplementedError
        self.part_id = part_id # Unique part ID e.g. Part1234
        self.source = source # Data source e.g. I3DR_DESKTOP_ABC123
        self.value = value # name of the image (NOT ImageValue)
        self.timestamp = timestamp
        # Values should be a list of ImageValues
        self.values = []
        for value in values:
            self.values.append(value.get_json())
        # Qualifying metadata should be a key value pair array e.g.
        # qualifying_metadata = [
        # 	{
        # 		"key": "key1",
        # 		"value": "value1"
        # 	},
        # 	{
        # 		"key": "key2",
        # 		"value": "value2"
        # 	}
        # ]
        self.qualifying_metadata = qualifying_metadata

    def get_json(self) -> dict:
        raise NotImplementedError
        # json = {
        # 	"part_id": self.part_id,
        # 	"value_id": self.value_id,
        # 	"source": self.source,
        # 	"values": self.values,
        # 	"qualifying_metadata": self.qualifying_metadata
        # }

# ML result data
# {
#  "part_id": "Part1234",
#  "source": "Analysis System",
#  "value": "Part1234_1.1_2.2_1.jpg",
#  "timestamp": "1516193959559",
#  "failures": [
#  {
#  "id": 124355435321576
#  "failure": "4711",
#  "position": [
#  44.2,
#  17.4
#  ],
#  "dimension": [
# Page 8 of 10
#  5.2,
#  1
#  ],
#  "qualifying_metadata": [
#  {
#  "key": "xxx",
#  "value": "1"
#  },
#  {
#  "key": "yyy",
#  "value": "2"
#  }
#  ]
#  },
#  {
#  "id": 124355435321578
#  "failure": "4712",
#  "position": [
#  33.2,
#  3
#  ],
#  "dimension": [
#  2.3,
#  1.1
#  ],
#  "qualifying_metadata": [
#  {
#  "key": "xxx",
#  "value": "1"
#  },
#  {
#  "key": "yyy",
#  "value": "2"
#  }
#  ]
#  }
#  ]
# }

# # Create a new resource
# response = requests.post('https://httpbin.org/post', data = {'key':'value'})
# # Update an existing resource
# requests.put('https://httpbin.org/put', data = {'key':'value'})
