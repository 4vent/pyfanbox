import json
from typing import Literal
from urllib import parse

import requests

from . import types


class CC_FANBOX_API():
    def __init__(self, FANBOXSESSID: str) -> None:
        self.sess = requests.Session()
        self.sess.cookies.set('FANBOXSESSID', FANBOXSESSID)
        self.sess.headers['Origin'] = 'https://www.fanbox.cc'
        res = self.sess.get('https://api.fanbox.cc/user.countUnreadMessages')
        if not res.status_code == 200:
            raise RuntimeError('Could not connect to Fanbox API! (Invalid cookie "FANBOXSESSID"?)')
        
        self.POST = _API_POST(self)
        self.CREATOR = _API_CREATOR(self)
        self.PLAN = _API_PLAN(self)
        self.TAG = _API_TAG(self)
        self.BELL = _API_BELL(self)
        self.USER = _API_USER(self)
        self.NEWSLETTER = _API_NEWSLETTER(self)
    
    def get(self, _url: str, **query) -> dict:
        if not _url.startswith('https://'):
            _url = 'https://api.fanbox.cc' + _url
        res = self.sess.get(_url + '?' + parse.urlencode(query, doseq=True))
        if not res.status_code == 200:
            raise RuntimeError('API access failed.', res.status_code, res.reason)
        return json.loads(res.content)
    
    @staticmethod
    def parse_qs(next_url):
        p = parse.urlparse(next_url)
        return parse.parse_qs(p.query)


class _CHILD_API():
    def __init__(self, api: CC_FANBOX_API) -> None:
        self._api = api


class _API_POST(_CHILD_API):
    def paginateCreator(self, creatorId: str):
        return types.APIPostPaginate(
            **self._api.get('/post.paginateCreator', creatorId=creatorId)
        )
    
    def listCreator(self, creatorId: str, maxPublishedDatetime: str,
                    maxId: str, limit: int):
        return types.APIPostListCreator(
            **self._api.get('/post.listCreator',
                            creatorId=creatorId,
                            maxPublishedDatetime=maxPublishedDatetime,
                            maxId=maxId,
                            limit=limit)
        )

    def info(self):
        pass
        # TODO
    
    def listComments(self):
        pass
        # TODO


class _API_CREATOR(_CHILD_API):
    def get(self, creatorId: str):
        return types.APICreatorGet(
            **self._api.get('/creator.get', creatorId=creatorId)
        )
    
    def listRecommended(self, limit=8):
        return types.APICreatorListRecommended(
            **self._api.get('/creator.listRecommended', limit=limit)
        )
    
    def listRelated(self, userId: str | int, limit=8,
                    method: Literal['diverse'] = 'diverse'):
        return types.APICreatorListRelated(
            **self._api.get('/creator.listRelated',
                            userId=userId, limit=limit, method=method)
        )


class _API_PLAN(_CHILD_API):
    def listCreator(self, creatorId: str):
        return types.APIPlanListCreator(
            **self._api.get('/plan.listCreator', creatorId=creatorId)
        )


class _API_TAG(_CHILD_API):
    def getFeatured(self, creatorId: str):
        return types.APITagGetFeatured(
            **self._api.get('/tag.getFeatured', creatorId=creatorId)
        )


class _API_BELL(_CHILD_API):
    def countUnread(self):
        return types.APIBellCountUnread(
            **self._api.get('/bell.countUnread')
        )


class _API_USER(_CHILD_API):
    def countUnreadMessages(self):
        return types.APICountUnreadMessages(
            **self._api.get('/user.countUnreadMessages')
        )


class _API_NEWSLETTER(_CHILD_API):
    def countUnreadMessages(self):
        return types.APINewsletterCountUnread(
            **self._api.get('/newsletter.countUnread')
        )