import json
import os

import requests

from . import types


def prepare_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    LOCALAPPDATA = os.getenv('LOCALAPPDATA')
    if LOCALAPPDATA is not None:
        CHROME_USER_DATA_PATH = LOCALAPPDATA + r'\Google\Chrome\User Data'
    else:
        raise RuntimeError('%LOCALAPPDATA% is None!!!')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])
    chrome_options.add_argument('--user-data-dir=' + CHROME_USER_DATA_PATH)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def get_fanbox_session_cookies() -> list[types.Cookie]:
    driver = prepare_driver()
    driver.get('https://accounts.pixiv.net/login'
               '?prompt=select_account'
               '&return_to=https%3A%2F%2Fwww.fanbox.cc%2Fauth%2Fstart'
               '&source=fanbox')
    input('Press enter after logging in to fanbox. >')
    return list(map(lambda x: types.Cookie(**x), driver.get_cookies()))


class SessionError(Exception):
    pass


def get_sessid(saved_cookie_path='cookie.json') -> str:
    session = requests.Session()
    session.headers['Origin'] = 'https://www.fanbox.cc'

    try:
        if not os.path.exists(saved_cookie_path):
            raise SessionError()

        with open(saved_cookie_path) as f:
            cookies = json.load(f)['cookies']
        
        for c in cookies:
            session.cookies.set(c['name'], c['value'])
        res = session.get('https://api.fanbox.cc/user.countUnreadMessages')
        if not res.status_code == 200:
            raise SessionError()
    except SessionError:
        cookies = get_fanbox_session_cookies()
        with open(saved_cookie_path, 'w') as f:
            json.dump({'cookies': cookies}, f)
    
    session.close()
    del session
    
    return [c for c in cookies if c['name'] == 'FANBOXSESSID'][0]['value']