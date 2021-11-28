# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hanimetv']

package_data = \
{'': ['*']}

install_requires = \
['requests', 'youtube_dl']

entry_points = \
{'console_scripts': ['htv = hanimetv.cli:main']}

setup_kwargs = {
    'name': 'hanimetv',
    'version': '1.2.1',
    'description': 'CLI downloader tool for hanime.tv',
    'long_description': '# hanimetv\nCLI tool for downloading hentai from hanime.tv\n## Installation\nInstall `ffmpeg` with whatever package manager you use, then run `pip install hanimetv`.\n## CLI Usage\n```\nusage: htv [-h] [--tags TAGS [TAGS ...]] [--broad-tag-match] [--blacklist BLACKLIST [BLACKLIST ...]] [--company COMPANY [COMPANY ...]] [--page PAGE] [--sort-by SORT_BY] [--sort-order SORT_ORDER] [--roll-search] [--resolution RESOLUTION] [--index INDEX [INDEX ...]] [--all] [--folder] [--franchise] [--url] [--metadata] [--verbose] [video ...]\n\npositional arguments:\n  video                 Video URL or search term\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --tags TAGS [TAGS ...], -t TAGS [TAGS ...]\n                        Tags to search for\n  --broad-tag-match     Match videos including any tags specified by --tags\n  --blacklist BLACKLIST [BLACKLIST ...], -b BLACKLIST [BLACKLIST ...]\n                        Blacklisted tags\n  --company COMPANY [COMPANY ...], -c COMPANY [COMPANY ...]\n                        Companies/brands to filter by\n  --page PAGE, -p PAGE  Page # of search results\n  --sort-by SORT_BY, -s SORT_BY\n                        Sorting method for search results ([u]pload, [v]iews, [l]ikes, [r]elease, [t]itle)\n  --sort-order SORT_ORDER, -w SORT_ORDER\n                        Order of sorting ([a]scending or [d]escending)\n  --roll-search, -R     Roll all search pages into one long page, useful for large-volume downloads\n  --resolution RESOLUTION, -r RESOLUTION\n                        Resolution of download, default 1080\n  --index INDEX [INDEX ...], -i INDEX [INDEX ...]\n                        Index of search results to download\n  --all, -a             Download all search results in page\n  --folder, -F          Create folders by franchise when downloading\n  --franchise, -f       Download the video and all other videos in its franchise\n  --url, -u             Show urls of the source video, do not download\n  --metadata, -m        Show metadata of the source video, do not download\n  --verbose, -v         Enable verbose logging for video download\n```\nThere are some special search terms you can use.\n - `htv ALL` - Shows all results matching filters\n - `htv random` - Random list of hentai\n - `htv new-uploads` - Shows the newest uploads\n - `htv new-releases` - Shows the newest releases\n## FAQ\n - Can this download 1080p videos without Premium?\n\nNot anymore. This utility used to be able to do this, but a breaking API change caused this functionality to stop working.\n - How do I download all videos matching a filter?\n\n`htv ALL -R -a <FILTER>` will do this.\nSome examples:\n\nDownload all videos from a brand:\n\n`htv ALL -R -a -c "<BRAND>"`\n\nDownload all videos matching a particular tag: \n\n`htv ALL -R -a -t "<TAG>"`\n - When I search for brand or tag XYZ, it shows empty search results\n \n If you are using tag, company, or blacklist filtering for search, you will need to make sure that the filters have quotes around them and are spelled correctly.\n \n Example: `htv ALL -c majin label` will show empty search results, but `htv ALL -c "magin label"` will show the correct results.\n- How can I send you death threats or feature requests?\n\nSend an email to rxqv@waifu.club and I probably won\'t read it unless you ask nicely.\n',
    'author': 'rxqv',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rxqv/htv',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
