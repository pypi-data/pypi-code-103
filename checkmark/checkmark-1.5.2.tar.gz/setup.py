# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['checkmark', 'checkmark.lists']

package_data = \
{'': ['*']}

install_requires = \
['pywebview>=3.5,<4.0']

setup_kwargs = {
    'name': 'checkmark',
    'version': '1.5.2',
    'description': 'Create launchable HTML form windows in Markdown',
    'long_description': '# Checkmark\n\nCheckmark lets you quickly and easily set up a way for you or any other user to submit data to your program through an HTML form. Using a Markdown-like document, you can specify a plethora of form elements.\n\n### Form elements\n\n- [Inlines](#inlines)\n    - [Label](#label)\n    - [Text & Textarea](#text-textarea)\n        - [Text](#text)\n        - [Textarea](#textarea)\n\n    - [Checkbox](#checkbox)\n    - [Button](#button)\n    \n- [Lists](#lists)\n    - [Radio buttons](#radio-buttons)\n    - [Dropdown menu](#dropdown-menu)\n\n\n## Example\n\n```py\nfrom checkmark import MarkdownForm\n\ndocument = """\n:[Username](username)\n>[Username](username "Ex. @user:domain.tld")\n:[Password](password)\n>[Password](password "Choose something not too simple.")\n\n<!-- A button that calls the `register` API method. -->\n@[Register](register)\n"""\n\nform = MarkdownForm(\n    title=\'My Markdown Form\',\n    document=document\n)\n\n# Define a function to be called\n# when you press the `Register` button.\n\n@form.api_method\ndef register(data):\n    username = data.get(\'username\', "")\n    password = data.get(\'password\', "")\n\n    print(f\'Successfully registered as {username}\')\n    print(f\'Your password is {"*" * len(password)}.\')\n\n@form.api_method\ndef save_settings(data):\n    layout = data.get(\'layout\', \'modern\')\n    language = data.get(\'language\', \'en\')\n\n    print(f"You\'ve chosen the {layout} layout.")\n    print(f\'Language: {language}\')\n\n    form.stop()\n\n\nform.start()\n```\n\nYou can try it out with the example below.\n\n```md\n# Account\n\n## Registration\n\n:[Username](username)\n>[Ex. @michael:duckduckgo.com](username "@user:domain.tld")<br>\n:[Password](password)\n>[password123](password "Choose something not too simple.")<br>\n:[Email](email)\n>[Ex. user@domain.tld](email "So that you can confirm your account.")<br>\n\n[x] [Sign me up to the newsletter](newsletter)\n\n>>[My hobbies are ...](hobbies "What do you like to do during your free time?")\n\n@[Register](register "Register new account.")\n\n\n## Settings\n\n## layout:\n* [IRC](irc)\n* [Modern](modern)\n* [Message bubbles](bubbles)\n\n## language:\n- [Swedish](se)\n- [English](en)\n- [French](fr)\n\n@[Save settings](save_settings)\n```\n\n\n## Rules\n\n### Inlines\n\nInline elements can be written anywhere on the line. As long as the pattern is matched, it should create an element in the right place.\n\n#### Link\n\n***This is not a custom element of its own.*** It\'s a description of how the standard Markdown link format is used within other custom elements.\n\nIn any and all definitions, if something looks like a Markdown link, it *is* a Markdown link and should be structured like one. It follows the same rules as regular Markdown and so the title is optional.\n\nThe title is always used as the `title` argument for any Checkmark element in which it is specified.\n\n```md\n[Text](url "Title.")\n```\n\n#### Label\n\nLabels are simply aesthetic and don\'t affect the functionality of the form.\nThe URL is only used to define the `for` argument.\n\n```md\n:[Super Label](best-label)\n```\n\n#### Text & TextArea\n\n`Text` uses one `>` as prefix and `TextArea` uses two.\nThe text of the link is used as the `placeholder` argument.\n\n##### TextArea\n```md\n>>[My hobbies are ...](hobbies "What do you like to do during your free time?")\n```\n\n##### Text\n```md\n>[Username](username "Ex. @user:domain.tld")\n```\n\n#### Checkbox\n```md\n[x] [I understand how checkboxes work.](understood)\n```\n\n#### Button\n\nCall one of the provided API methods using a button, with the URL as the function name.\n\n```md\n@[Log in](log_in)\n```\n\n### Lists\n\nA list has a variable name and the possible values for it. The variable name is defined by a preceding heading\'s Markdown link URL. The URLs of the entries are used for the values. Any empty lines terminate the list, whether between entries or the entries and the heading.\n\n#### Radio Buttons\n\nRadio button entries use `*` as prefix.\n\n```md\n## [Message layout](layout):\n* [IRC](irc)\n* [Modern](modern)\n* [Message bubbles](bubbles)\n```\n\n#### Dropdown Menu\n\nDropdown menu entries use `-` as prefix.\n\n```md\n## [Language](language):\n- [Swedish](se)\n- [English](en)\n- [French](fr)\n```\n\n#### Extensible List (Not yet implemented)\n\nI will be adding lists that allow you to define multiple types of elements per entry and with a `+` button, you will be able to add new multi-element entries into the list.\n\nThe future syntax will look a little something like this:\n\n```md\n# advanced-dns:\n+ ## type:\n  - [A Record](a)\n  - [CNAME Record](cname)\n  - [TXT Record](txt)\n+ >[Host](host)\n+ >[Port](port)\n+ [x] [Backward compatible](backcomp)\n```\n\nThis list would include a dropdown menu, two text inputs, and a checkbox.\nI\'ll describe it more in detail once I get it implemented.',
    'author': 'Maximillian Strand',
    'author_email': 'maximillian.strand@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/deepadmax/checkmark',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
