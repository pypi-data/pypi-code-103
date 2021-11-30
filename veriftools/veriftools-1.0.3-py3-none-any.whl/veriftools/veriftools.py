import requests
import time
import shutil

def download_image(url: str, filename: str) -> None:
    print('> Dowloading')
    res = requests.get(url, stream = True)
    if res.status_code == 200:
        with open(filename,'wb') as f:
            shutil.copyfileobj(res.raw, f) 
        print('  - Image sucessfully downloaded: ', filename)
    else:
        print('  - Image couldn\'t be retrieved')

def generate_image(generator_url: str, user: dict, data: dict, images: dict) -> str:
    l = generator_url.split('/')
    BASE_URL = l[0] + '//' + l[2] + '/'
    print('> Authorization')
    LOGIN_URL = BASE_URL + 'login/'
    client = requests.session()
    client.get(LOGIN_URL)  # sets cookie
    csrftoken = client.cookies['csrftoken']

    login_data = dict(username=user['login'], password=user['password'], csrfmiddlewaretoken=csrftoken, next='/')
    resp = client.post(LOGIN_URL, data=login_data, headers=dict(Referer=LOGIN_URL))
    print("  - Authorization sucessfully") if "Log out" in resp.text else print("< Authorization failed")

    client.get(generator_url)  # sets cookie
    csrftoken = client.cookies['csrftoken']

    print('> Sending Data')
    images_cp = images.copy()
    data_cp = data.copy()
    for img in images: images_cp[img] = open(images[img], 'rb')

    data_cp['csrfmiddlewaretoken'] = csrftoken;
    data_cp['next'] = '/'

    resp = client.post(generator_url, files=images_cp, data=data_cp, headers=dict(Referer=generator_url))
    if resp.json()['status'] == 'FAIL': print('  - GOOGLE_RECAPTCHA ERROR. YOU NEED TO HAVE MORE THEN $30 ON BALANCE!\n', resp.json()); return ''

    id = resp.json()["id"]
    task_id = resp.json()["task_id"]
    print(f'  - Task with ID: {id} sucessfully created')

    print('> Processing')
    code = '' 
    for i in range(40):
        status = requests.get(f'{BASE_URL}get-result/?id={id}&task_id={task_id}').json()['status']
        if status != code: code = status; print('  - ', status)
        if status == 'END': break
        time.sleep(2)
    else:
        print('  - SERVER ERROR!')
        return ''


    print('> Purchase')
    URLadd = BASE_URL + "cart/add/"
    login_data = dict(generatorItemId=id, csrfmiddlewaretoken=csrftoken, next='/')
    client.post(URLadd, data=login_data, headers=dict(Referer=URLadd))

    BUY_URL = BASE_URL + "cart/buy/"
    resp = client.post(BUY_URL, data=login_data, headers=dict(Referer=BUY_URL))
    task_id = resp.json()['task_id']
    if resp.json()['status'] != 'SUCCESS': print('  - ERRR. PURCHASE FAILED!'); return ''
    print('  - Sucessfully')

    return  BASE_URL + requests.get(f'{BASE_URL}get-result/?id={str(id)}&task_id={str(task_id)}').json()['image_url']


