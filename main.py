import os
import asyncio
import requests
import zipfile

from settings import Settings


class File:
    file_name = None
    file_link = ''
    file_path = ''
    uploaded = False


def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '..')))


def get_token():
    url = f"https://api.selcdn.ru/auth/v1.0"

    header = {
        'X-Auth-User': Settings.STORAGE_AUTH_USER,
        'X-Auth-Key': Settings.STORAGE_AUTH_KEY,
    }

    payload = {}
    response = requests.request("GET", url, headers=header, data=payload)

    return response.headers['x-storage-token']


headers = {
    'X-Auth-Token': f'{get_token()}',
    'X-Delete-After': '9999999999999999999999999'
}


def update_status(item: File):
    try:
        item.uploaded = True
    except Exception as e:
        print(e)


async def upload_file(data: File):
    item = data


    if item.file_link:
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), item.file_name)

        request = requests.get(item.file_link)

        with open(path, 'wb') as file:
            file.write(request.content)
    else:
        path = item.file_path

    print(item.file_name)

    url = f"https://api.selcdn.ru/v1/SEL_{Settings.STORAGE_CONTAINER_USER}/{Settings.STORAGE_CONTAINER}/{item.file_name}"

    with open(path, 'rb') as f:
        content = f.read()

    payload = {}
    files = [
        (item.file_name, (item.file_name, content))
    ]

    response = requests.request("PUT", url, headers=headers, data=payload, files=files)

    if response.status_code == 201:
        print("uploaded")
        os.remove(path)
        update_status(item)
    else:
        print(response)
        print(response.text)
