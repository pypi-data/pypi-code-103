# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['featurestorebundle',
 'featurestorebundle.db',
 'featurestorebundle.delta',
 'featurestorebundle.entity',
 'featurestorebundle.feature',
 'featurestorebundle.feature.writer',
 'featurestorebundle.metadata',
 'featurestorebundle.notebook.decorator',
 'featurestorebundle.notebook.decorator.tests',
 'featurestorebundle.test',
 'featurestorebundle.windows']

package_data = \
{'': ['*'], 'featurestorebundle': ['_config/*']}

install_requires = \
['daipe-core>=1.0.0,<2.0.0', 'pyfony-bundles>=0.4.0,<0.5.0']

entry_points = \
{'pyfony.bundle': ['create = '
                   'featurestorebundle.FeatureStoreBundle:FeatureStoreBundle']}

setup_kwargs = {
    'name': 'feature-store-bundle',
    'version': '1.1.1.dev10',
    'description': 'Feature Store for the Daipe AI Platform',
    'long_description': '# Feature Store bundle\n\n**This package is distributed under the "DataSentics SW packages Terms of Use." See [license](https://raw.githubusercontent.com/daipe-ai/feature-store-bundle/master/LICENSE)**\n\nFeature store bundle allows you to store features with metadata.\n\n# Installation\n\n```bash\npoetry add feature-store-bundle\n```\n\n# Getting started\n\n\n1. Define entity and custom `feature decorator`\n\n```python\nfrom pyspark.sql import types as t\nfrom daipecore.decorator.DecoratedDecorator import DecoratedDecorator\nfrom featurestorebundle.entity.Entity import Entity\nfrom featurestorebundle.feature.FeaturesStorage import FeaturesStorage\nfrom featurestorebundle.notebook.decorator.feature import feature\n\nentity = Entity(\n    name="client",\n    id_column="UserName",\n    id_column_type=t.StringType(),\n    time_column="run_date",\n    time_column_type=t.DateType(),\n)\n\n@DecoratedDecorator\nclass client_feature(feature):  # noqa N081\n    def __init__(self, *args, category=None):\n        super().__init__(*args, entity=entity, category=category, features_storage=features_storage)\n```\n\n2. Use the `feature decorator` to save features as you create them\n\n```python\nfrom pyspark.sql import functions as f\nfrom pyspark.sql import DataFrame\nfrom datalakebundle.imports import transformation, read_table\n\n@transformation(read_table("silver.tbl_loans"), display=True)\n@client_feature(\n    ("Age", "Client\'s age"),\n    ("Gender", "Client\'s gender"),\n    ("WorkExperience", "Client\'s work experience"),\n    category="personal",\n)\ndef client_personal_features(df: DataFrame):\n    return (\n        df.select("UserName", "Age", "Gender", "WorkExperience")\n        .groupBy("UserName")\n        .agg(\n            f.max("Age").alias("Age"),\n            f.first("Gender").alias("Gender"),\n            f.first("WorkExperience").alias("WorkExperience"),\n        )\n        .withColumn("run_date", f.lit(today))\n    )\n```\n\n3. Write/Merge all features in one go\n\n```python\nfrom datalakebundle.imports import notebook_function\nfrom featurestorebundle.delta.DeltaWriter import DeltaWriter\n\nnotebook_function()\ndef write_features(writer: DeltaWriter):\n    writer.write_latest(features_storage)\n```\n',
    'author': 'Datasentics',
    'author_email': 'jiri.koutny@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daipe-ai/feature-store-bundle',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
