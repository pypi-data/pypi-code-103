import os
try:
    # Python 2 support
    from base64 import encodestring
except ImportError:
    # Python 3.9.0+ support
    from base64 import encodebytes as encodestring

translations = {}

types = {0: ".mo", 1: ".po"}

for i in range(0, 2):
    file_name = "base{0}".format(types[i])
    print(file_name)

    current_path, _ = os.path.split(__file__) 
    file_path = os.path.join(current_path, file_name)
    print(current_path)

    file = open(file_path, 'rb')
    file_read = file.read()
    file_64_encode = encodestring(file_read)

    translations[i] = file_64_encode

#print(images)
f = open("dict_translations.txt", "w")
f.write(str(translations))
f.close()