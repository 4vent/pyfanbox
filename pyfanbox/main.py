import json
import os
from urllib import parse

import requests

import .types


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


def get_fanbox_session_cookies():
    driver = prepare_driver()
    driver.get('https://accounts.pixiv.net/login'
               '?prompt=select_account'
               '&return_to=https%3A%2F%2Fwww.fanbox.cc%2Fauth%2Fstart'
               '&source=fanbox')
    input('Press enter after logging in to fanbox. >')
    return driver.get_cookies()


class CC_FANBOX_API():
    def __init__(self, FANBOXSESSID: str) -> None:
        self.sess = requests.Session()
        self.sess.cookies.set('FANBOXSESSID', FANBOXSESSID)
        self.sess.headers['Origin'] = 'https://www.fanbox.cc'
        res = self.sess.get('https://api.fanbox.cc/user.countUnreadMessages')
        if not res.status_code == 200:
            raise RuntimeError('Could not connect to Fanbox API! (Invalid cookie "FANBOXSESSID"?)')
        
        self.POST = _API_POST(self)
    
    def get(self, _url, **query) -> dict:
        res = self.sess.get(_url + '?' + parse.urlencode(query, doseq=True))
        if not res.status_code == 200:
            raise RuntimeError('API access failed.', res.status_code, res.reason)
        return json.loads(res.content)
    
    @staticmethod
    def parse_url(url):
        p = parse.urlparse(url)
        return {
            '_url': p.scheme + '://' + p.netloc + p.path,
            **parse.parse_qs(p.query)
        }


class _API_POST():
    def __init__(self, api: CC_FANBOX_API) -> None:
        self.__api = api
    
    def paginateCreator(self, creatorId: str | None = None, *, next_url: str | None = None):
        if next_url:
            return self.__api.get(next_url)
        else:
            return self.__api.get('https://api.fanbox.cc/post.paginateCreator',
                                  creatorId=creatorId)