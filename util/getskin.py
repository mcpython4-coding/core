# file licensed under the licence in licenses/LICENSE_mcskinview
# modified for this project

import io
import sys
import json
import shutil

from base64 import b64decode

import requests
import globals as G

DEBUG = False
SIMULATE = False

userid_url = "https://api.mojang.com/users/profiles/minecraft/{username}"
userinfo_url = "https://sessionserver.mojang.com/session/minecraft/profile/{userid}"


class SimulatedResponse(object):
    def __init__(self, content, is_json, raw=None):
        self.content = content
        self.is_json = is_json
        self.status_code = 200
        self.raw = raw

    def json(self):
        if self.is_json:
            return json.loads(self.content)
        return None


def fail(msg, verbose_msg):
    print(msg, file=sys.stderr)
    if DEBUG:
        print(verbose_msg, file=sys.stderr)
    sys.exit(1)


def find_texture_info(properties):
    for prop in properties:
        if prop['name'] == 'textures':
            return json.loads(b64decode(prop['value'], validate=True).decode('utf-8'))
    return None


def get_url(url, **kwargs):
    if SIMULATE:
        content = None
        is_json = False
        raw = None
        # These files are not provided in the git repo because I consider them
        # kind of sensitive.  Feel free to provide your own in their place.
        if url.startswith('https://api.mojang.com/users/profiles/minecraft/'):
            with open('simulated_userid_response.json', 'r') as f:
                content = f.read()
            is_json = True
        elif url.startswith('https://sessionserver.mojang.com/session/minecraft/profile/'):
            with open('simulated_userinfo_response.json', 'r') as f:
                content = f.read()
            is_json = True
        else:
            with open('simulated_skin_response.png', 'rb') as f:
                content = f.read()
            is_json = False
            raw = io.BytesIO(content)
        return SimulatedResponse(content, is_json, raw)
    else:
        return requests.get(url, **kwargs)


def download_skin(username):

    r = get_url(userid_url.format(username=username))
    if r.status_code != 200: raise ValueError()
    userid = r.json()['id']

    r = get_url(userinfo_url.format(userid=userid))
    userinfo = r.json()
    texture_info = find_texture_info(userinfo['properties'])
    if texture_info is None: raise ValueError()

    try:
        skin_url = texture_info['textures']['SKIN']['url']
    except:
        raise ValueError() from None
    r = get_url(skin_url, stream=True)
    if r.status_code != 200: raise ValueError()
    with open(G.tmp.name+"/skin.png", 'wb') as f:
        shutil.copyfileobj(r.raw, f)

