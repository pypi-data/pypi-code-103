# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pbspark']

package_data = \
{'': ['*']}

install_requires = \
['protobuf>=3.19.1,<4.0.0', 'pyspark>=3.2.0,<4.0.0']

setup_kwargs = {
    'name': 'pbspark',
    'version': '0.1.0',
    'description': 'Decode protobuf messages into spark dataframes',
    'long_description': '# pbspark\n\nThis package provides a way to deserialize protobuf messages into pyspark dataframes using a pyspark udf.\n\n## Installation\n\nTo install:\n\n```bash\npip install pbspark\n```\n\n## Usage\n\nSuppose we have a pyspark DataFrame which contains a column `value` which has protobuf encoded messages of our `SimpleMessage`:\n\n```protobuf\nsyntax = "proto3";\n\npackage example;\n\nmessage SimpleMessage {\n  string name = 1;\n  int64 quantity = 2;\n  float measure = 3;\n}\n```\n\nUsing `pbspark` we can decode the messages into spark `StructType` and then flatten them.\n\n```python\nfrom pyspark.sql.session import SparkSession\nfrom pbspark import MessageConverter\nfrom example.example_pb2 import SimpleMessage\n\nspark = SparkSession.builder.getOrCreate()\n\nexample = SimpleMessage(name="hello", quantity=5, measure=12.3)\ndata = [{"value": example.SerializeToString()}]\ndf = spark.createDataFrame(data)\n\nmc = MessageConverter()\ndf_decoded = df.select(mc.from_protobuf(df.value, SimpleMessage).alias("value"))\ndf_flattened = df_decoded.select("value.*")\ndf_flattened.show()\n\n# +-----+--------+-------+\n# | name|quantity|measure|\n# +-----+--------+-------+\n# |hello|       5|   12.3|\n# +-----+--------+-------+\n\ndf_flattened.schema\n# StructType(List(StructField(name,StringType,true),StructField(quantity,IntegerType,true),StructField(measure,FloatType,true))\n```\n\nBy default, protobuf\'s `MessageToDict` serializes everything into JSON compatible objects. To handle custom serialization of other types, for instance `google.protobuf.Timestamp`, you can use a custom serializer.\n\nSuppose we have a message in which we want to combine fields when we serialize.\n\nCreate and register a custom serializer with the `MessageSerializer`.\n\n```python\nfrom pbspark import MessageConverter\nfrom example.example_pb2 import ExampleMessage\nfrom example.example_pb2 import NestedMessage\nfrom pyspark.sql.types import StringType\n\nmc = MessageConverter()\n# built-in to serialize Timestamp messages to datetime objects\nmc.register_timestamp_serializer()\n\n# register a custom serializer\n# this will serialize the NestedMessages into a string rather than a\n# struct with `key` and `value` fields\ncombine_key_value = lambda message: message.key + ":" + message.value\n\nmc.register_serializer(NestedMessage, combine_key_value, StringType)\n\n...\n\nfrom pyspark.sql.session import SparkSession\nfrom pyspark import SparkContext\nfrom pyspark.serializers import CloudPickleSerializer\n\nsc = SparkContext(serializer=CloudPickleSerializer())\nspark = SparkSession(sc).builder.getOrCreate()\n\nmessage = ExampleMessage(nested=NestedMessage(key="hello", value="world"))\ndata = [{"value": message.SerializeToString()}]\ndf = spark.createDataFrame(data)\n\ndf_decoded = df.select(mc.from_protobuf(df.value, ExampleMessage).alias("value"))\n# rather than a struct the value of `nested` is a string\ndf_decoded.select("value.nested").show()\n# +-----------+\n# |     nested|\n# +-----------+\n# |hello:world|\n# +-----------+\n\n```',
    'author': 'flynn',
    'author_email': 'crf204@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/crflynn/pbspark',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
