# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oarepo_model_builder',
 'oarepo_model_builder.builders',
 'oarepo_model_builder.invenio',
 'oarepo_model_builder.loaders',
 'oarepo_model_builder.model_preprocessors',
 'oarepo_model_builder.outputs',
 'oarepo_model_builder.property_preprocessors',
 'oarepo_model_builder.templates',
 'oarepo_model_builder.utils']

package_data = \
{'': ['*'], 'oarepo_model_builder.invenio': ['templates/*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0',
 'black>=21.11b1,<22.0',
 'click>=7.1',
 'deepdiff>=5.6.0,<6.0.0',
 'isort>=5.10.1,<6.0.0',
 'jsonpointer>=2.2,<3.0',
 'libcst>=0.3.19,<0.4.0',
 'munch>=2.5.0,<3.0.0',
 'tomlkit>=0.7.2,<0.8.0']

extras_require = \
{'json5': ['json5>=0.9.6,<0.10.0'], 'pyyaml': ['PyYAML>=6.0,<7.0']}

entry_points = \
{'console_scripts': ['oarepo-compile-model = oarepo_model_builder.cli:run'],
 'oarepo_model_builder.builders': ['020-jsonschema = '
                                   'oarepo_model_builder.builders.jsonschema:JSONSchemaBuilder',
                                   '030-mapping = '
                                   'oarepo_model_builder.builders.mapping:MappingBuilder',
                                   '100-python_structure = '
                                   'oarepo_model_builder.builders.python_structure:PythonStructureBuilder',
                                   '110-invenio_record = '
                                   'oarepo_model_builder.invenio.invenio_record:InvenioRecordBuilder',
                                   '120-invenio_record_metadata = '
                                   'oarepo_model_builder.invenio.invenio_record_metadata:InvenioRecordMetadataBuilder',
                                   '130-invenio_record_schema = '
                                   'oarepo_model_builder.invenio.invenio_record_schema:InvenioRecordSchemaBuilder',
                                   '200-invenio_record_permissions = '
                                   'oarepo_model_builder.invenio.invenio_record_permissions:InvenioRecordPermissionsBuilder',
                                   '300-invenio_record_search_options = '
                                   'oarepo_model_builder.invenio.invenio_record_search:InvenioRecordSearchOptionsBuilder',
                                   '310-invenio_record_service_config = '
                                   'oarepo_model_builder.invenio.invenio_record_service_config:InvenioRecordServiceConfigBuilder',
                                   '320-invenio_record_service = '
                                   'oarepo_model_builder.invenio.invenio_record_service:InvenioRecordServiceBuilder',
                                   '340-invenio_record_dumper = '
                                   'oarepo_model_builder.invenio.invenio_record_dumper:InvenioRecordDumperBuilder',
                                   '400-invenio_record_resource_config = '
                                   'oarepo_model_builder.invenio.invenio_record_resource_config:InvenioRecordResourceConfigBuilder',
                                   '410-invenio_record_resource = '
                                   'oarepo_model_builder.invenio.invenio_record_resource:InvenioRecordResourceBuilder',
                                   '420-invenio_blueprint = '
                                   'oarepo_model_builder.invenio.invenio_blueprint:InvenioBlueprintBuilder',
                                   '900-invenio_sample_app_poetry = '
                                   'oarepo_model_builder.invenio.invenio_sample_app_poetry:InvenioSampleAppPoetryBuilder',
                                   '910-invenio_record_metadata_alembic_poetry '
                                   '= '
                                   'oarepo_model_builder.invenio.invenio_record_metadata_alembic_poetry:InvenioRecordMetadataAlembicPoetryBuilder',
                                   '920-invenio_record_metadata_models_poetry '
                                   '= '
                                   'oarepo_model_builder.invenio.invenio_record_metadata_models_poetry:InvenioRecordMetadataModelsPoetryBuilder',
                                   '930-invenio_resource_poetry = '
                                   'oarepo_model_builder.invenio.invenio_record_resource_poetry:InvenioRecordResourcePoetryBuilder',
                                   '940-invenio_record_search_poetry = '
                                   'oarepo_model_builder.invenio.invenio_record_search_poetry:InvenioRecordSearchPoetryBuilder',
                                   '950-invenio_record_jsonschemas_poetry = '
                                   'oarepo_model_builder.invenio.invenio_record_jsonschemas_poetry:InvenioRecordJSONSchemasPoetryBuilder'],
 'oarepo_model_builder.loaders': ['json = '
                                  'oarepo_model_builder.loaders:json_loader',
                                  'json5 = '
                                  'oarepo_model_builder.loaders:json_loader',
                                  'yaml = '
                                  'oarepo_model_builder.loaders:yaml_loader',
                                  'yml = '
                                  'oarepo_model_builder.loaders:yaml_loader'],
 'oarepo_model_builder.model_preprocessors': ['01-default = '
                                              'oarepo_model_builder.model_preprocessors.default_values:DefaultValuesModelPreprocessor',
                                              '10-invenio = '
                                              'oarepo_model_builder.model_preprocessors.invenio:InvenioModelPreprocessor',
                                              '20-elasticsearch = '
                                              'oarepo_model_builder.model_preprocessors.elasticsearch:ElasticsearchModelPreprocessor'],
 'oarepo_model_builder.ouptuts': ['jsonschema = '
                                  'oarepo_model_builder.outputs.jsonschema:JSONSchemaOutput',
                                  'mapping = '
                                  'oarepo_model_builder.outputs.mapping:MappingOutput',
                                  'python = '
                                  'oarepo_model_builder.outputs.python:PythonOutput',
                                  'toml = '
                                  'oarepo_model_builder.outputs.toml:TOMLOutput'],
 'oarepo_model_builder.property_preprocessors': ['10-text_keyword = '
                                                 'oarepo_model_builder.property_preprocessors.text_keyword:TextKeywordPreprocessor'],
 'oarepo_model_builder.templates': ['99-base_templates = '
                                    'oarepo_model_builder.invenio']}

setup_kwargs = {
    'name': 'oarepo-model-builder',
    'version': '0.9.0',
    'description': 'An utility library that generates OARepo required data model files from a JSON specification file',
    'long_description': '# OARepo model builder\n\nA library and command-line tool to generate invenio model from a single model file.\n\n## CLI Usage\n\n```bash\noarepo-compile-model model.yaml\n```\n\nwill compile the model.yaml into the current directory. Options:\n\n```bash\n  --output-directory <dir> Output directory where the generated files will be\n                           placed. Defaults to "."\n  --package <name>         Package into which the model is generated. If not\n                           passed, the name of the current directory,\n                           converted into python package name, is used.\n  --set <name=value>       Overwrite option in the model file. \n                           Example --set settings.elasticsearch.keyword-ignore-above=20\n  -v                       Increase the verbosity. This option can be used\n                           multiple times.\n  --config <filename>      Load a config file and replace parts of the model\n                           with it. The config file can be a json, yaml or a\n                           python file. If it is a python file, it is\n                           evaluated with the current model stored in the\n                           "oarepo_model" global variable and after the\n                           evaluation all globals are set on the model.\n  --isort / --skip-isort   Call isort on generated sources (default: yes)\n  --black / --skip-black   Call black on generated sources (default: yes)\n```\n\n## Model file structure\n\nA model is a json/yaml file with the following structure:\n\n```yaml\nsettings:\n  python:\n  elasticsearch:\nmodel:\n  properties:\n    title: { type: \'fulltext\' }\n```\n\nThere might be more sections (documentation etc.), but only the ``settings`` and ``model`` are currently processed.\n\n### settings section\n\nThe settings section might contain the following keys\n(default values below):\n\n```yaml\nsettings:\n  package: basename(output dir) with \'-\' converted to \'_\'\n  kebap-package: to_kebap(package)\n  package-path: path to package as python Path instance\n  schema-version: 1.0.0\n  schema-name: { kebap-package }-{schema-version}.json\n  schema-file: full path to generated json schema\n  mapping-file: full path to generated mapping\n  collection-url: camel_case(last component of package)\n\n  processing-order: [ \'settings\', \'*\', \'model\' ]\n\n  python:\n    record-prefix: camel_case(last component of package)\n    templates: { }   # overridden templates\n    marshmallow:\n      top-level-metadata: true\n      mapping: { }\n\n    record-prefix-snake: snake_case(record_prefix)\n\n    record-class: { settings.package }.record.{record_prefix}Record\n      # full record class name with package\n    record-schema-class: { settings.package }.schema.{record_prefix}Schema\n      # full record schema class name (apart from invenio stuff, contains only metadata field)\n    record-schema-metadata-class: { settings.package }.schema.{record_prefix}MetadataSchema\n      # full record schema metadata class name (contains model schema as marshmallow)\n    record-schema-metadata-alembic: { settings.package_base }\n    # name of key in pyproject.toml invenio_db.alembic entry point \n    record-metadata-class: { settings.package }.metadata.{record_prefix}Metadata\n      # db class to store record\'s metadata \n    record-metadata-table-name: { record_prefix.lower() }_metadata\n      # name of database table for storing metadata \n    record-permissions-class: { settings.package }.permissions.{record_prefix}PermissionPolicy\n      # class containing permissions for the record\n    record-dumper-class: { settings.package }.dumper.{record_prefix}Dumper\n      # record dumper class for elasticsearch\n    record-search-options-class: { settings.package }.search_options.{record_prefix}SearchOptions\n      # search options for the record\n    record-service-config-class: { settings.package }.service_config.{record_prefix}ServiceConfig\n      # configuration of record\'s service\n    record-resource-config-class: { settings.package }.resource.{record_prefix}ResourceConfig\n      # configuration of record\'s resource\n    record-resource-class: { settings.package }.resource.{record_prefix}Resource\n      # record resource\n    record-resource-blueprint-name: { record_prefix }\n    # blueprint name of the resource \n    register-blueprint-function: { settings.package }.blueprint.register_blueprint\'\n      # name of the blueprint registration function\n\n  elasticsearch:\n    keyword-ignore-above: 50\n\n  plugins:\n    packages: [ ]\n    # list of extra packages that should be installed in compiler\'s venv\n    output|builder|model|property:\n      # plugin types - file outputs, builders, model preprocessors, property preprocessors \n      disabled: [ ]\n      # list of plugin names to disable\n      # string "__all__" to disable all plugins in this category    \n      enabled:\n      # list of plugin names to enable. The plugins will be used\n      # in the order defined. Use with disabled: __all__\n      # list of "module:className" that will be added at the end of\n      # plugin list\n```\n\n### model section\n\nThe model section is a json schema that might be annotated with extra sections. For example:\n\n```yaml\nmodel:\n  properties:\n    title:\n      type: multilingual\n      oarepo:ui:\n        label: Title\n        class: bold-text\n      oarepo:documentation: |\n        Lorem ipsum ...\n        Dolor sit ...\n```\n\n**Note**: ``multilingual`` is a special type (not defined in this library) that is translated to the correct schema,\nmapping and marshmallow files with a custom ``PropertyPreprocessor``.\n\n``oarepo:ui`` gives information for the ui output\n\n``oarepo:documentation`` is a section that is currently ignored\n\n## Referencing a model\n\n## API Usage\n\nTo generate invenio model from a model file, perform the following steps:\n\n1. Load the model into a ``ModelSchema`` instance\n    ```python\n    from oarepo_model_builder.schema import ModelSchema\n    from oarepo_model_builder.loaders import yaml_loader\n   \n    included_models = {\n        \'my_model\': lambda parent_model: {\'test\': \'abc\'} \n    }\n    loaders = {\'yaml\': yaml_loader}\n   \n    model = ModelSchema(file_path=\'test.yaml\', \n                        included_models=included_models, \n                        loaders=loaders)\n    ```\n\n   You can also path directly the content of the file path in ``content`` attribute\n\n   The ``included_models`` is a mapping between model key and its accessor. It is used to replace any ``oarepo:use``\n   element. See the Referencing a model above.\n\n   The ``loaders`` handle loading of files - the key is lowercased file extension, value a function taking (schema,\n   path) and returning loaded content\n\n\n2. Create an instance of ``ModelBuilder``\n\n   To use the pre-installed set of builders and preprocessors, invoke:\n\n   ```python\n   from oarepo_model_builder.entrypoints \\ \n    import create_builder_from_entrypoints\n   \n   builder = create_builder_from_entrypoints()\n   ```\n\n   To have a complete control of builders and preprocessors, invoke:\n\n   ```python\n      from oarepo_model_builder.builder import ModelBuilder\n      from oarepo_model_builder.builders.jsonschema import JSONSchemaBuilder\n      from oarepo_model_builder.builders.mapping import MappingBuilder\n      from oarepo_model_builder.outputs.jsonschema import JSONSchemaOutput\n      from oarepo_model_builder.outputs.mapping import MappingOutput\n      from oarepo_model_builder.outputs.python import PythonOutput\n      from oarepo_model_builder.property_preprocessors.text_keyword import TextKeywordPreprocessor\n      from oarepo_model_builder.model_preprocessors.default_values import DefaultValuesModelPreprocessor\n      from oarepo_model_builder.model_preprocessors.elasticsearch import ElasticsearchModelPreprocessor\n\n      builder = ModelBuilder(\n        output_builders=[JSONSchemaBuilder, MappingBuilder],\n        outputs=[JSONSchemaOutput, MappingOutput, PythonOutput],\n        model_preprocessors=[DefaultValuesModelPreprocessor, ElasticsearchModelPreprocessor],\n        property_preprocessors=[TextKeywordPreprocessor]\n      )    \n   ```   \n\n\n3. Invoke\n\n   ```python\n      builder.build(schema, output_directory)\n   ```\n\n## Extending the builder\n\n### Builder pipeline\n\n![Pipeline](./docs/oarepo-model-builder.png)\n\nAt first, an instance of [ModelSchema](./oarepo_model_builder/schema.py) is obtained. The schema can be either passed\nthe content of the schema as text, or just a path pointing to the file. The extension of the file determines\nwhich [loader](./oarepo_model_builder/loaders/__init__.py) is used. JSON, JSON5 and YAML are supported out of the box (\nif you have json5 and pyyaml packages installed)\n\nThen [ModelBuilder](./oarepo_model_builder/builder.py).build(schema, output_dir) is called.\n\nIt begins with calling all [ModelPreprocessors](./oarepo_model_builder/model_preprocessors/__init__.py). They get the\nwhole schema and settings and can modify both.\nSee [ElasticsearchModelPreprocessor](./oarepo_model_builder/model_preprocessors/elasticsearch.py) as an example. The\ndeepmerge function does not overwrite values if they already exist in settings.\n\nFor each of the outputs (jsonschema, mapping, record, resource, ...)\nthe top-level properties of the transformed schema are then iterated. \nThe order of the top-level properties is given by ``settings.processing-order``.\n\nThe top-level property and all its descendants (a visitor patern, visiting property by property), \na [PropertyPreprocessor](./oarepo_model_builder/property_preprocessors/__init__.py)\nis called. \n\nThe preprocessor can either modify the property, decide to remove it or replace it with a new set of properties\n(see [multilang in tests](./tests/multilang.py) ).\n\nThe property is then passed to the\n[OutputBuilder](./oarepo_model_builder/builders/__init__.py)\n(an example is [JSONSchemaBuilder](./oarepo_model_builder/builders/jsonschema.py))\nthat serializes the tree of properties into the output.\n\nThe output builder does not create files on the filesystem explicitly but uses instances\nof [OutputBase](./oarepo_model_builder/outputs/__init__.py), for\nexample [JSONOutput](./oarepo_model_builder/outputs/json.py) or more\nspecialized [JSONSchemaOutput](./oarepo_model_builder/outputs/jsonschema.py).\n\nSee [JSONBaseBuilder](./oarepo_model_builder/builders/json_base.py) for an example of how to get an output and write to\nit (in this case, the json-based output).\n\nThis way, even if more output builders access the same file, their access is coordinated.\n\n### Registering Preprocessors, Builders and Outputs for commandline client\n\nThe model & property preprocessors, output builders and outputs are registered in entry points. In poetry, it looks as:\n\n```toml\n[tool.poetry.plugins."oarepo_model_builder.builders"]\n010-jsonschema = "oarepo_model_builder.builders.jsonschema:JSONSchemaBuilder"\n020-mapping = "oarepo_model_builder.builders.mapping:MappingBuilder"\n030-python_structure = "oarepo_model_builder.builders.python_structure:PythonStructureBuilder"\n040-invenio_record = "oarepo_model_builder.invenio.invenio_record:InvenioRecordBuilder"\n\n[tool.poetry.plugins."oarepo_model_builder.ouptuts"]\njsonschema = "oarepo_model_builder.outputs.jsonschema:JSONSchemaOutput"\nmapping = "oarepo_model_builder.outputs.mapping:MappingOutput"\npython = "oarepo_model_builder.outputs.python:PythonOutput"\n\n[tool.poetry.plugins."oarepo_model_builder.property_preprocessors"]\n010-text_keyword = "oarepo_model_builder.preprocessors.text_keyword:TextKeywordPreprocessor"\n\n[tool.poetry.plugins."oarepo_model_builder.model_preprocessors"]\n01-default = "oarepo_model_builder.transformers.default_values:DefaultValuesModelPreprocessor"\n10-invenio = "oarepo_model_builder.transformers.invenio:InvenioModelPreprocessor"\n20-elasticsearch = "oarepo_model_builder.transformers.elasticsearch:ElasticsearchModelPreprocessor"\n\n[tool.poetry.plugins."oarepo_model_builder.loaders"]\njson = "oarepo_model_builder.loaders:json_loader"\njson5 = "oarepo_model_builder.loaders:json_loader"\nyaml = "oarepo_model_builder.loaders:yaml_loader"\nyml = "oarepo_model_builder.loaders:yaml_loader"\n\n[tool.poetry.plugins."oarepo_model_builder.templates"]\n99-base_templates = "oarepo_model_builder.invenio.templates"\n```\n\n### Generating python files\n\nThe default python output is based on [libCST](https://github.com/Instagram/LibCST) that enables merging generated code\nwith a code that is already present in output files. The transformer provided in this package can:\n\n1. Add imports\n2. Add a new class or function on top-level\n3. Add a new method to an existing class\n4. Add a new const/property to an existing class\n\nThe transformer will not touch an existing function/method. Increase verbosity level to get a list of rejected patches\nor add ``--set settings.python.overwrite=true``\n(use with caution, with sources stored in git and do diff afterwards).\n\n#### Overriding default templates\n\nThe default templates are written as jinja2-based templates.\n\nTo override a single or multiple templates, create a package containing the templates and register it\nin ``oarepo_model_builder.templates``. Be sure to specify the registration key smaller than ``99-``. The template loader\niterates the sorted set of keys and your templates would be loaded before the default ones. Example:\n\n   ```\n   my_package\n      +-- __init__.py\n      +-- templates\n          +-- invenio_record.py.jinja2 \n   ```\n\n   ```python\n   # my_package/__init__.py\nTEMPLATES = {\n    # resolved relative to the package\n    "record": "templates/invenio_record.py.jinja2"\n}\n   ```\n\n   ```toml\n   [tool.poetry.plugins."oarepo_model_builder.templates"]\n20-my_templates = "my_package"\n   ```\n\nTo override a template for a single model, in your model file (or configuration file with -c option or via --set option)\n, specify the relative path to the template:\n\n```yaml\nsettings:\n  python:\n    templates:\n      record: ./test/my_invenio_record.py.jinja2\n```\n',
    'author': 'Miroslav Bauer',
    'author_email': 'bauer@cesnet.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
