from datetime import datetime, timedelta, timezone
from . import types
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pyfanbox.main import CC_FANBOX_API


class utility():
    def __init__(self, api: 'CC_FANBOX_API') -> None:
        self.__api = api
    
    def supporting_creators(self):
        current_supportings: list[types._Payment_Creator] = []

        payments = self.__api.PAYMENT.listPaid()
        now = datetime.now(timezone(timedelta(hours=9)))
        for p in payments.body:
            payDT = datetime.fromisoformat(p.paymentDatetime)
            if payDT.year == now.year and payDT.month == now.month:
                current_supportings.append(p.creator)
        
        return current_supportings
    
    def get_browsable_posts(self, user_id: str):
        browsable_posts: list[types._PostItem] = []
        
        urls = self.__api.POST.paginateCreator(user_id).body
        for url in urls:
            postList = self.__api.POST.listCreator(**self.__api.parse_qs(url)).body.items
            for post in postList:
                if not post.isRestricted:
                    browsable_posts.append(post)
        
        return browsable_posts

    @staticmethod
    def format_blog(body: types._PostInfoBody, creatorId: str):
        text = ''
        if isinstance(body.blocks, type):
            return body.text
        for block in body.blocks:
            if isinstance(block, types._ArticleParagraphBlock):
                t = ''
                insertion = {}
                if not isinstance(block.styles, type):
                    for style in reversed(block.styles):
                        b, e = style.offset, style.offset + style.length
                        insertion[b] = ' **'
                        insertion[e] = '** '
                if not isinstance(block.links, type):
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
            elif isinstance(block, types._ArticleHeaderBlock):
                text += ('\n\n### ' + block.text + '\n\n')
            elif isinstance(block, types._ArticleImageBlock):
                text += ('{image:' + block.imageId + '}\n\n')
            elif isinstance(block, types._ArticleFileBlock):
                text += ('{file:' + block.fileId + '}\n\n')
            elif isinstance(block, types._ArticleURLEmbedBlock):
                if isinstance(body.urlEmbedMap, type):
                    raise AttributeError('body.urlEmbedMap is not defined!')
                urlEmbed = body.urlEmbedMap[block.urlEmbedId]
                if isinstance(urlEmbed, types._UrlEmbedDefault):
                    url = urlEmbed.url
                    text += (f'[{url}]({url})\n\n')
                elif isinstance(urlEmbed, types._UrlEmbedHtml):
                    html = urlEmbed.html
                    text += (html)
                elif isinstance(urlEmbed, types._UrlEmbedHtmlCard):
                    html = urlEmbed.html
                    text += (html)
                elif isinstance(urlEmbed, types._UrlEmbedFanboxCreator):
                    creator_id = urlEmbed.profile.creatorId
                    url = 'https://' + creator_id + '.fanbox.cc/'
                    text += (f'[FANBOX CREATOR]({url})\n\n')
                elif isinstance(urlEmbed, types._UrlEmbedFanboxPost):
                    post_id = urlEmbed.postInfo.id
                    url = 'https://' + creatorId + '.fanbox.cc/posts/' + post_id
                    text += (f'[FANBOX POST]({url})\n\n')
                else:
                    text += ('! - UNKNOWN FORMAT OF URL EMBED - !\n\n')
            else:
                text += ('! - UNKNOWN FORMAT OF BLOCK - !\n\n')
        
        return text