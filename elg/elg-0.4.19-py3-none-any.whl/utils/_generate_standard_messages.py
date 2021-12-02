import configparser
import json

"""
Fairly basic script to generate elg/model/base/StandardMessages.
Left simple to make maintenance/editing easy.

To run from the root directory of this project: `python elg/utils/generate_standard_messages.py`.
"""
config = configparser.RawConfigParser()
# Don't lower-case the keys
config.optionxform = lambda x: x
config.read("elg/model/messages/errors.ini")
details_dicts = {lang: dict(config.items(lang)) for lang in config.sections()}

# Revert the dicts to pass from:
# 	"{'es': {1: 'q', 2: 'w'}, 'en': {1: 's', 2: 'r'}}"
# to
# 	"{1: {'es': 'q', 'en: 's'}, 2: {'es: 'w', 'en: 'r'}}"
keys = list(details_dicts.values())[0].keys()
details_dicts_reverted = {k: {} for k in keys}
for lang, d in details_dicts.items():
    # assert all the dict have the same keys
    assert d.keys() == keys
    for k in keys:
        details_dicts_reverted[k][lang] = d[k]

with open("elg/model/base/StandardMessages.py", "w+") as file:
    file.write("from .StatusMessage import StatusMessage\n\n")
    file.write("\nclass StandardMessages:\n")
    file.write(
        '\n\t"""\n'
        + "\tThis class provides easy access to the standard set of ELG status messages that are provided by default by \n"
        + "\tthe platform and should be fully translated in the ELG user interface. If you use codes other than these \n"
        + "\tstandard ones in your services then you should also try to contribute translations of your messages into as \n"
        + "\tmany languages as possible for the benefit of other ELG users.\n\n"
        "\tImplementation note: This class is auto-generated from elg-messages.properties - to add new message codes you \n"
        + "\tshould edit the property files, then run /utils/generate_standard_messages.py. Do not edit this class directly.\n"
        + '\t"""\n'
    )
    for key in details_dicts_reverted:
        file.write("\n\t@classmethod")
        file.write("\n\tdef generate_" + key.replace(".", "_").lower() + '(cls, params=[], detail={}, lang="en"):')
        file.write('\n\t\t"""Generate StatusMessage for code: ' + key + '"""')
        file.write('\n\t\tcode="' + key + '"')
        file.write("\n\t\ttext=" + json.dumps(details_dicts_reverted[key]))
        file.write("\n\t\treturn StatusMessage(code=code,text=text[lang],params=params,detail=detail)")
        file.write("\n")
