import requests

link = 'https://raw.githubusercontent.com/devvspaces/readme_template/master/README.md'

def gen():
    return requests.get(url=link).text


if __name__ == "__main__":
    print('Calling the gen func')
    print(gen())