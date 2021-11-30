# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyriksprot',
 'pyriksprot.dehyphenation',
 'pyriksprot.foss',
 'pyriksprot.parlaclarin',
 'pyriksprot.parlaclarin.resources',
 'pyriksprot.parlaclarin.resources.templates',
 'pyriksprot.scripts',
 'pyriksprot.tagged_corpus']

package_data = \
{'': ['*'], 'pyriksprot.parlaclarin.resources': ['xslt/*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'Unidecode>=1.3.2,<2.0.0',
 'click>=7.1.2,<8.0.0',
 'loguru>=0.5.3,<0.6.0',
 'lz4>=3.1.3,<4.0.0',
 'pandas>=1.2.3,<2.0.0',
 'pdoc>=8.0.0,<9.0.0',
 'pytest-codeblocks>=0.11.3,<0.12.0',
 'requests>=2.26.0,<3.0.0',
 'tqdm>=4.62.3,<5.0.0']

entry_points = \
{'console_scripts': ['riksprot2any = pyriksprot.scripts.riksprot2any:main',
                     'riksprot2text = pyriksprot.scripts.riksprot2text:main',
                     'riksprot2tfs = pyriksprot.scripts.riksprot2tfs:main']}

setup_kwargs = {
    'name': 'pyriksprot',
    'version': '2021.9.8',
    'description': 'Python API for Riksdagens Protokoll',
    'long_description': '# Python package for reading and tagging Riksdagens Protokoll\n\nBatteries (tagger) not included.\n\n## Overview\n\nThis package is intended to cover the following use cases:\n\n### Extract "text documents" from the Parla-CLARIN XML files\n\nText can be extracted from the XML files at different granularity (paragraphs, utterance, speech, who, protocol). The text can be grouped (combined) into larger temporal blocks based on time (year, lustrum, decade or custom periods). Within each of these block the text in turn can be grouped by speaker attributes (who, party, gender).\n\nThe text extraction can done using the `riksprot2text` utility, which is a CLI interface installed with the package, or in Python code using the API that this package exposes. The Python API exposed both streaming (SAX based) methods and a domain model API (i.e. Python classes representing protocols, speeches and utterances).\n\nBoth the CLI and the API supports dehyphenation using method described in [Anföranden: Annotated and Augmented Parliamentary Debates from Sweden, Stian Rødven Eide, 2020](https://gup.ub.gu.se/publication/302449). The API also supports user defined text transformations.\n\n### Extract PoS-tagged versions of the Parla-CLARIN XML files\n\nPart-of-speech tagged versions of the protocols can be extracted with the same granularity and aggregation as described above for the raw text. The returned documents are tab-separated files with fields for text, baseform and pos-tag (UPOS, XPOS). Note that the actual part-of-speech tagging is done using tools found in the `pyriksprot_tagging` repository ([link](https://github.com/welfare-state-analytics/westac_parlaclarin_pipeline)).\n\nCurrently there are no open-source tagged versions of the corpos avaliable. The tagging is done using [Stanza](https://stanfordnlp.github.io/stanza/) with Swedish language models produced and made publically avaliable by Språkbanken Text.\n\n### Store extracted text\n\nThe extracted text can be stored as optionally compressed plain text files on disk, or in a ZIP-archive.\n\n## Pre-requisites\n\n- Python >=3.8\n- A folder containing the Riksdagen Protokoll (parliamentary protocols) Github repository.\n\n```bash\ncd some-folder \\\ngit clone --branch "specify-branch" --depth 1 https://github.com/welfare-state-analytics/riksdagen-corpus.git\ncd riksdagen-corpus\ngit config core.quotepath off\n\n```\n\n## Installation (Linux)\n\nCreate an new isolated virtual environment for pyriksprot:\n\n```bash\nmkdir /path/to/new/pyriksprot-folder\ncd /path/to/new/pyriksprot-folder\npython -m venv .venv\n```\n\nActivate the environment:\n\n```bash\ncd /path/to/new/pyriksprot-folder\nsource .venv/bin/activate\n```\n\nInstall `pyriksprot` in activated virtual environment.\n\n```bash\npip install pyriksprot\n```\n\n## CLI riksprot2text:  Extract aggregated text corpus from Parla-CLARIN XML files\n\n```bash\n\nλ riksprot2text --help\n\nUsage: riksprot2text [OPTIONS] SOURCE_FOLDER TARGET\n\nOptions:\n  -m, --mode [plain|zip|gzip|bz2|lzma]\n                                  Target type\n  -t, --temporal-key TEXT         Temporal partition key(s)\n  -y, --years TEXT                Years to include in output\n  -g, --group-key TEXT            Partition key(s)\n  -p, --processes INTEGER RANGE   Number of processes to use\n  -l, --segment-level [protocol|speech|utterance|paragraph|who]\n                                  Protocol extract segment level\n  -e, --keep-order                Keep output in filename order (slower, multiproc)\n\n  -s, --skip-size INTEGER RANGE   Skip blocks of char length less than\n  -d, --dedent                    Remove indentation\n  -k, --dehyphen                  Dehyphen text\n  --help                          Show this message and exit.\n\n```\n\n### Examples CLI\n\nAggregate text per year grouped by speaker. Store result in a single zip. Skip documents less than 50 characters.\n\n```python\nriksprot2text /path/to/corpus output.zip -m zip -t year -l protocol -g who --skip-size 50\n```\n\nAggregate text per decade grouped by speaker. Store result in a single zip. Remove indentations and hyphenations.\n\n```bash\nriksprot2text /path/to/corpus output.zip -m zip -t decade -l who -g who --dedent --dehyphen\n```\n\nAggregate text using customized temporal periods and grouped by party.\n\n```bash\nriksprot2text /path/to/corpus output.zip -m zip -t "1920-1938,1929-1945,1946-1989,1990-2020" -l who -g party\n```\n\nAggregate text per document and group by gender and party.\n\n```bash\nriksprot2text /path/to/corpus output.zip -m zip -t protocol -l who -g party -g gender\n```\n\nAggregate text per year grouped by gender and party and include only 1946-1989.\n\n```bash\nriksprot2text /path/to/corpus output.zip -m zip -t year -l who -g party -g gender -y 1946-1989\n```\n\n## Python API - Iterate XML protocols\n\nAggregate text per year grouped by speaker. Store result in a single zip. Skip documents less than 50 characters.\n\n<!--pytest-codeblocks:skip-->\n```python\nimport pyriksprot\n\ntarget_filename: str = f\'output.zip\'\nopts = {\n    \'source_folder\': \'/path/to/corpus\',\n    \'target\': \'outout.zip\',\n    \'target_mode\': TargetType.Zip,\n    \'segment_level\': SegmentLevel.Who,\n    \'dedent\': True,\n    \'dehyphen\': False,\n    \'years\': \'1955-1965\',\n    \'temporal_key\': TemporalKey.Protocol,\n    \'group_keys\': (GroupingKey.Party, GroupingKey.Gender),\n}\n\npyriksprot.extract_corpus_text(**opts)\n\n```\n\n\nIterate over protocol and speaker:\n\n```python\n\nfrom pyriksprot import interface, iterstors\n\nitems: Iterable[interface.ProtocolSegment] = iterators.XmlProtocolTextIterator(\n    filenames=filenames, segment_level=SegmentLevel.Who, segment_skip_size=0, processes=4\n)\n\nfor item in items:\n    print(item.who, len(item.text))\n\n```\n\nIterate over protocol and speech, skip empty:\n\n```python\n\nfrom pyriksprot import interface, iterstors\n\nitems: Iterable[interface.ProtocolSegment] = iterators.XmlProtocolTextIterator(\n    filenames=filenames, segment_level=SegmentLevel.Who, segment_skip_size=1, processes=4\n)\n\nfor item in items:\n    print(item.who, len(item.text))\n\n```\n\nIterate over protocol and speech, apply preprocess function(s):\n\n```python\n\nfrom pyriksprot import interface, iterstors\nimport ftfy  # pip install ftfy\nimport unidecode\n\nfix_text: Callable[[str], str] = pyriksprot.compose(\n    [str.lower, pyriksprot.dedent, ftfy.fix_character_width, unidecode.unidecode ]\n)\nitems: Iterable[interface.ProtocolSegment] = iterators.XmlProtocolTextIterator(\n    filenames=filenames, segment_level=SegmentLevel.Speech, segment_skip_size=1, processes=4, preprocessor=fix_text,\n)\n\nfor item in items:\n    print(item.who, len(item.text))\n\n```\n\n## Python API - Iterate protocols as domain entities\n\n## CLI riksprot2tags:  Extract aggregated part-of-speech tagged corpus\n',
    'author': 'Roger Mähler',
    'author_email': 'roger.mahler@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://westac.se',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '==3.8.5',
}


setup(**setup_kwargs)
