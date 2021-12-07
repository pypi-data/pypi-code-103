import sys
import string
import pkg_resources


def greet(name):
    filename = pkg_resources.resource_filename('mypackage', 'template.txt')
    with open(filename) as f:
        template = string.Template(f.read())
    print(template.safe_substitute({'name': name}))    
    
def greet_main():
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = 'unknown human'
    greet(name)
