import json
import os
from datetime import datetime
from typing import Any

import requests

import pyfanbox


def _testout(data: str | bytes | dict[Any, Any]):
    filename = datetime.now().isoformat().replace(':', '-')
    if isinstance(data, dict):
        with open(filename + '.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    else:
        try:
            data = json.loads(data)
            with open(filename + '.json', 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            with open(filename + '.txt', 'w') as f:
                f.write(data)  # type: ignore


class SessionError(Exception):
    pass


def get_sessid() -> str:
    session = requests.Session()
    session.headers['Origin'] = 'https://www.fanbox.cc'

    try:
        if not os.path.exists('cookie.json'):
            raise SessionError()

        with open('cookie.json') as f:
            cookies = json.load(f)['cookies']
        
        for c in cookies:
            session.cookies.set(c['name'], c['value'])
        res = session.get('https://api.fanbox.cc/user.countUnreadMessages')
        if not res.status_code == 200:
            raise SessionError()
    except SessionError:
        cookies = pyfanbox.get_fanbox_session_cookies()
        with open('cookie.json', 'w') as f:
            json.dump({'cookies': cookies}, f)
    
    session.close()
    del session
    
    return [c for c in cookies if c['name'] == 'FANBOXSESSID'][0]['value']


def main2():
    FANBOXSESSID = get_sessid()
    api = pyfanbox.CC_FANBOX_API(FANBOXSESSID)
    _testout(dict(api.POST.paginateCreator('devildance')))
    api.POST.paginateCreator('devildance')


main2()
