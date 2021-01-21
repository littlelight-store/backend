from time import sleep

import requests


def get_all_progressions():
    url = "https://www.bungie.net/Platform/Destiny2/2/Profile/4611686018471738848/"

    querystring = {"components": "Profiles,CharacterProgressions,200"}

    headers = {
        'X-API-Key': "840cc4a823fe4f1ab3480fb034c3f650",
        'User-Agent': "PostmanRuntime/7.19.0",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "7a7d5b41-a0e8-4e4a-9f0b-6f9c2884aef6,01ea6da7-ecb4-403e-b59d-371ceb9d7ad9",
        'Host': "www.bungie.net",
        'Accept-Encoding': "gzip, deflate",
        'Cookie': "bungled=1564876795285261145; bungledid=BzuOON6dQuhIn/P7TYb6IoifeDNnzr3XCAAA; __cfduid=da3095f727b79964be1484c60872552401586892847; Q6dA7j3mn3WPBQVV6Vru5CbQXv0q+I9ddZfGro+PognXQwjW=v1Y9hRgw@@7SX",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    if response.ok:
        return response.json()["Response"]["characterProgressions"]["data"]


def get_progression_info(hash_id):
    url = f"https://www.bungie.net/Platform/Destiny2/Manifest/DestinyProgressionDefinition/{hash_id}/"

    headers = {
        'X-API-Key': "840cc4a823fe4f1ab3480fb034c3f650",
        'User-Agent': "PostmanRuntime/7.19.0",
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Postman-Token': "a0974d29-cae2-484e-aef3-19ff7121a58f,2aa8937f-63db-4c44-a9e4-4cc07d009979",
        'Host': "www.bungie.net",
        'Accept-Encoding': "gzip, deflate",
        'Cookie': "bungled=1564876795285261145; bungledid=BzuOON6dQuhIn/P7TYb6IoifeDNnzr3XCAAA; __cfduid=da3095f727b79964be1484c60872552401586892847; Q6dA7j3mn3WPBQVV6Vru5CbQXv0q+I9ddZfGro+PognXQwjW=v1Y9hRgw@@7SX",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers)

    if response.ok:
        return response.json()["Response"]


if __name__ == '__main__':
    print('starting')
    progressions = get_all_progressions()

    first_key = list(progressions.keys())[0]

    progression = progressions[first_key]['progressions']

    for k, _ in progression.items():
        progression = get_progression_info(k)
        sleep(2)
        print(progression["displayProperties"], k)

