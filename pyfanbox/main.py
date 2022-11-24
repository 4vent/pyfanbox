import json
from typing import Literal
from urllib import parse

import requests

from . import types, utility


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
        self.PAYMENT = _API_PAYMENT(self)
        self.util = utility.utility(self)
    
    def get(self, _url: str, **query) -> dict:
        if not _url.startswith('https://'):
            _url = 'https://api.fanbox.cc' + _url
        if '?' not in _url and not len(query.keys()) == 0:
            _url = _url + '?' + parse.urlencode(query, doseq=True)
        res = self.sess.get(_url)

        if not res.status_code == 200:
            raise RuntimeError('API access failed.', res.status_code, res.reason)
        return json.loads(res.content)
    
    def download(self, url, stream: bool = True):
        res = self.sess.get(url, stream=stream)
        return res
    
    @staticmethod
    def parse_qs(url: str | types.URL):
        parsed = parse.urlparse(url)
        query = parse.parse_qs(parsed.query)
        return {k: v[0] for k, v in query.items()}
    
    @staticmethod
    def format_blog(body: types._PostInfoBody, creatorId: str):
        
        text = ''
        for block in body.blocks:
            if block.type == 'p':
                t = ''
                insertion = {}
                if block.styles is not types.UNDEFINED:
                    for style in reversed(block.styles):
                        b, e = style.offset, style.offset + style.length
                        insertion[b] = ' **'
                        insertion[e] = '** '
                if block.links is not types.UNDEFINED:
                    for link in reversed(block.links):
                        b, e = link.offset, link.offset + link.length
                        if b in insertion:
                            if insertion[b] == ' **':
                                insertion[b] = ' **['
                            elif insertion[b] == '** ':
                                insertion[b] = '** ['
                            else:
                                insertion[b] = '['
                        else:
                            insertion[b] = '['
                        if e in insertion:
                            if insertion[e] == ' **':
                                insertion[e] = '](' + link.url + ') **'
                            elif insertion[e] == '** ':
                                insertion[e] = '](' + link.url + ')** '
                            else:
                                insertion[e] = '](' + link.url + ')'
                        else:
                            insertion[e] = '](' + link.url + ')'
                insertion = dict(sorted(insertion.items()))

                prev = 0
                for k, v in insertion.items():
                    t += block.text[prev:k]
                    t += v
                    prev = k
                t += block.text[prev:]
                text += (t + '\n\n')
            elif block.type == 'header':
                text += ('\n\n### ' + block.text + '\n\n')
            elif block.type == 'image':
                text += ('{image:' + block.imageId + '}\n\n')
            elif block.type == 'file':
                text += ('{file:' + block.fileId + '}\n\n')
            elif block.type == 'url_embed':
                if body.urlEmbedMap[block.urlEmbedId].type == 'fanbox.post':
                    post_id = body.urlEmbedMap[block.urlEmbedId].postInfo.id
                    text += ('[FANBOX POST](https://' + creatorId + '.fanbox.cc/posts/' + post_id + ')\n\n')
                else:
                    text += (body.urlEmbedMap[block.urlEmbedId].html + '\n\n')
            else:
                text += ('! - UNKNOWN FORMAT OF BLOCK - !\n\n')
        
        return text


class _CHILD_API():
    def __init__(self, api: CC_FANBOX_API) -> None:
        self._api = api


class _API_POST(_CHILD_API):
    def paginateCreator(self, creatorId: str):
        return types.APIPostPaginate(
            **self._api.get('/post.paginateCreator', creatorId=creatorId)
        )
    
    def listCreator(self, creatorId: str, maxPublishedDatetime: str,
                    maxId: str, limit: int | str):
        return types.APIPostListCreator(
            **self._api.get('/post.listCreator',
                            creatorId=creatorId,
                            maxPublishedDatetime=maxPublishedDatetime,
                            maxId=maxId,
                            limit=limit)
        )

    def info(self, postId: int | str):
        return types.APIPostInfo(
            **self._api.get('/post.info', postId=postId)
        )
    
    def listComments(self, postId: int | str, limit=10):
        return types.APIPostListComments(
            **self._api.get('/post.listComments', postId=postId, limit=limit)
        )


class _API_CREATOR(_CHILD_API):
    def get(self, creatorId: str):
        return types.APICreatorGet(
            **self._api.get('/creator.get', creatorId=creatorId)
        )
    
    def listRecommended(self, limit=8):
        return types.APICreatorList(
            **self._api.get('/creator.listRecommended', limit=limit)
        )
    
    def listRelated(self, userId: str | int, limit=8,
                    method: Literal['diverse'] = 'diverse'):
        return types.APICreatorList(
            **self._api.get('/creator.listRelated',
                            userId=userId, limit=limit, method=method)
        )
    
    def listFollowing(self):
        return types.APICreatorList(
            **self._api.get('/creator.listFollowing')
        )


class _API_PLAN(_CHILD_API):
    def listCreator(self, creatorId: str):
        return types.APIPlanList(
            **self._api.get('/plan.listCreator', creatorId=creatorId)
        )
    
    def listSupporting(self):
        return types.APIPlanList(
            **self._api.get('/plan.listSupporting')
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
        return types.APIUserCountUnreadMessages(
            **self._api.get('/user.countUnreadMessages')
        )


class _API_NEWSLETTER(_CHILD_API):
    def countUnreadMessages(self):
        return types.APINewsletterCountUnread(
            **self._api.get('/newsletter.countUnread')
        )


class _API_PAYMENT(_CHILD_API):
    def listPaid(self):
        return types.APIPaymentList(
            **self._api.get('/payment.listPaid')
        )
    
    def listUnpaid(self):
        return types.APIPaymentList(
            **self._api.get('/payment.listUnpaid')
        )