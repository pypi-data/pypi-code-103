# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pg_data_etl',
 'pg_data_etl.database',
 'pg_data_etl.database.actions',
 'pg_data_etl.database.actions.query',
 'pg_data_etl.helpers',
 'pg_data_etl.settings']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pg = pg_data_etl.cli:main']}

setup_kwargs = {
    'name': 'pg-data-etl',
    'version': '0.3.4',
    'description': 'ETL tools for spatial data stored in postgres',
    'long_description': '# pg-data-etl\n\n[![PyPI](https://img.shields.io/pypi/v/pg-data-etl?style=for-the-badge)](https://pypi.org/project/pg-data-etl/)\n\nETL tools for spatial data stored in postgres.\n\n## About\n\nThis module exists to make life easier when working with geospatial data in a Postgres database.\n\nYou should have the following command-line tools installed, preferably on your system path:\n\n- `psql`\n- `pg_dump`\n- `shp2postgis`\n- `ogr2ogr`\n\nIf you want to use the optional vector tile functions you\'ll also need:\n\n- `tippecanoe`\n\n## Installation\n\n`pip install pg_data_etl`\n\n## Example\n\nThe following code blocks import spatial data into Postgres and runs a spatial query:\n\n### 1) Connect to the database and create it\n\n```python\n>>> from pg_data_etl import Database\n>>> credentials = {\n...     "db_name": "sample_database",\n...     "host": "localhost",\n...     "un": "username",\n...     "pw": "my-password",\n...     "super_un": "postgres",\n...     "super_pw": "superuser-password"\n... }\n>>> db = Database.from_parameters(**credentials)\n>>> db.admin("CREATE")\n```\n\n### 2) Import GIS data from the web\n\n```python\n>>> data_to_import = [\n...     ("philly.high_injury_network", "https://phl.carto.com/api/v2/sql?filename=high_injury_network_2020&format=geojson&skipfields=cartodb_id&q=SELECT+*+FROM+high_injury_network_2020"),\n...     ("philly.playgrounds", "https://opendata.arcgis.com/datasets/899c807e205244278b3f39421be8489c_0.geojson")\n... ]\n>>> for sql_tablename, source_url in data_to_import:\n...     kwargs = {\n...         "filepath": source_url,\n...         "sql_tablename": sql_tablename,\n...         "gpd_kwargs": {"if_exists":"replace"}\n...     }\n...     db.import_gis(**kwargs)\n```\n\n### 3) Run a query and get the result as a `geopandas.GeoDataFrame`\n\n```python\n>>> # Define a SQL query as a string in Python\n>>> query = """\n... select * from philly.high_injury_network\n... where st_dwithin(\n...     st_transform(geom, 26918),\n...     (select st_transform(st_collect(geom), 26918) from philly.playgrounds),\n...     100\n... )\n... order by st_length(geom) DESC """\n>>> # Get a geodataframe from the db using the query\n>>> gdf = db.gdf(query)\n>>> gdf.head()\n   index  objectid            street_name   buffer                                               geom  uid\n0    234       189          BUSTLETON AVE  75 feet  LINESTRING (-75.07081 40.03528, -75.07052 40.0...  236\n1     65        38                 5TH ST  50 feet  LINESTRING (-75.14528 39.96913, -75.14502 39.9...   66\n2    223       179           ARAMINGO AVE  75 feet  LINESTRING (-75.12212 39.97449, -75.12132 39.9...  224\n3    148       215               KELLY DR  75 feet  LINESTRING (-75.18470 39.96934, -75.18513 39.9...  150\n4    156       224  MARTIN LUTHER KING DR  75 feet  LINESTRING (-75.17713 39.96327, -75.17775 39.9...  159\n```\n\nTo save time and typing, database credentials can be stored in a text file. You can place this file wherever you want,\nbut by default it\'s placed into `/USERHOME/.pg-data-etl/database_connections.cfg`.\n\nTo generate one for the first time, run the following from a terminal prompt:\n\n```shell\n> pg make-config-file\n```\n\nThis file uses the following format:\n\n```\n[DEFAULT]\npw = this-is-a-placeholder-password\nport = 5432\nsuper_db = postgres\nsuper_un = postgres\nsuper_pw = this-is-another-placeholder-password\n\n[localhost]\nhost = localhost\nun = postgres\npw = your-password-here\n```\n\nEach entry in square brackets is a named connection, and any parameters not explicitly defined are inherited from `DEFAULT`.\nYou can have as many connections defined as you\'d like, and you can use them like this:\n\n```python\n>>> from pg_data_etl import Database\n>>> db = Database.from_config("sample_database", "localhost")\n```\n\n## Development\n\nClone or fork this repo:\n\n```bash\ngit clone https://github.com/aaronfraint/pg-data-etl.git\ncd pg-data-etl\n```\n\nInstall an editable version with `poetry`:\n\n```bash\npoetry install\n```\n\nWindows users who prefer to use `conda` can use the included `environment.yml` file:\n\n```bash\nconda env create -f environment.yml\n```\n',
    'author': 'Aaron Fraint',
    'author_email': '38364429+aaronfraint@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aaronfraint/pg-data-etl',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
