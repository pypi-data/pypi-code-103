import requests


def buscar_avatar(usuario):
    """Buscar o avatar de um usuário no Github
    :param usuario: str com o nome de usuario da conta git
    :return: str com o link do avatar
    """
    url= f'https://api.github.com/users/{usuario}'
    resp = requests.get(url)
    avatar =resp.json()['avatar_url']
    criado_em = resp.json()['created_at']
    update = resp.json()['updated_at']
    return avatar,criado_em,update
if __name__ == '__main__':
    print(buscar_avatar('cyaconquista'))