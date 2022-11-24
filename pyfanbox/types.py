import json
import warnings
from typing import Any, Literal, NewType, Type, TypeVar, TypedDict, overload

from . import pyfanbox_enum as pfenum

UNDEFINED = type('UNDEFINED', (object,), {})

URL = NewType('URL', str)
ISODateTime = NewType('ISODateTime', str)

_API_RESPONCE = TypeVar('_API_RESPONCE')
_ENUM_LIKE = TypeVar('_ENUM_LIKE')
_ENUM_VAL = TypeVar('_ENUM_VAL')


@overload
def maplist(__list: list[dict[Any, Any]], cls: Type[_API_RESPONCE]) -> list[_API_RESPONCE]: ...
@overload
def maplist(__list: Type[UNDEFINED], cls: Any) -> Type[UNDEFINED]: ...
@overload
def maplist(__list: None, cls: Any) -> None: ...


def maplist(__list: None | Type[UNDEFINED] | list[dict[Any, Any]],
            cls: Type[_API_RESPONCE]
            ) -> None | Type[UNDEFINED] | list[_API_RESPONCE]:
    if isinstance(__list, type):
        if __list == UNDEFINED:
            return UNDEFINED
        else:
            raise ValueError(f'arg "__list" allow "None or UNDEFINED or dict" but get "{type(__list)}"')
    elif __list is None:
        return None
    else:
        return list(map(lambda x: cls(**x), __list))


@overload
def mapdict(__dict: dict[str, dict[Any, Any]], cls: Type[_API_RESPONCE]) -> dict[str, _API_RESPONCE]: ...
@overload
def mapdict(__dict: Type[UNDEFINED], cls: Any) -> Type[UNDEFINED]: ...
@overload
def mapdict(__dict: None, cls: Any) -> None: ...


def mapdict(__dict: dict[str, dict[Any, Any]] | Type[UNDEFINED] | None,
            cls: Type[_API_RESPONCE]
            ) -> None | Type[UNDEFINED] | dict[str, _API_RESPONCE]:
    if isinstance(__dict, type):
        if __dict == UNDEFINED:
            return UNDEFINED
        else:
            raise ValueError(f'arg "__dict" allow "None or UNDEFINED or dict" but get "{type(__dict)}"')
    elif __dict is None:
        return None
    else:
        return {k: cls(**v) for k, v in __dict.items()}


@overload
def setclass(__dict: dict[Any, Any], cls: Type[_API_RESPONCE]) -> _API_RESPONCE: ...
@overload
def setclass(__dict: Type[UNDEFINED], cls: Any) -> Type[UNDEFINED]: ...
@overload
def setclass(__dict: None, cls: Any) -> None: ...


def setclass(__dict: None | Type[UNDEFINED] | dict[Any, Any],
             cls: Type[_API_RESPONCE]
             ) -> None | Type[UNDEFINED] | _API_RESPONCE:
    if isinstance(__dict, type):
        if __dict == UNDEFINED:
            return UNDEFINED
        else:
            raise ValueError(f'arg "__dict" allow "None or UNDEFINED or dict" but get "{type(__dict)}"')
    elif __dict is None:
        return None
    else:
        return cls(**__dict)


@overload
def safe_enum(val: _ENUM_VAL, enum: Type[_ENUM_LIKE]) -> _ENUM_LIKE | _ENUM_VAL: ...
@overload
def safe_enum(val: Type[UNDEFINED], enum: Any) -> Type[UNDEFINED]: ...
@overload
def safe_enum(val: None, enum: Any) -> None: ...


def safe_enum(val: None | Type[UNDEFINED] | _ENUM_VAL, enum: Type[_ENUM_LIKE]
              ) -> None | Type[UNDEFINED] | _ENUM_LIKE | _ENUM_VAL:
    if val == UNDEFINED:
        return UNDEFINED
    elif val is None:
        return None
    else:
        try:
            return enum(val)
        except ValueError:
            warnings.warn(f"SafeEnum: '{val}' is not a valid {enum.__name__}. Assignd {type(val)} value.")
            return val


class Cookie(TypedDict):
    domain: str
    expiry: int
    httpOnly: bool
    name: str
    path: str
    secure: bool
    value: str


class FanboxJSONEncoder(json.encoder.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, APIResponce):
            return {k: v for k, v in o.__dict__.items()
                    if k not in [] and not v == UNDEFINED}
        else:
            return super().default(o)


class APIResponce():
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            warnings.warn(f'Unknown Key "{k}" in <{type(self).__name__}>. (Module bug or Updated Fanbox API.) '
                          'You can use this key but there is no autocomplete.')
            setattr(self, k, v)


# === API Body Element ===

class _User(APIResponce):
    def __init__(self, userId: str,
                 name: str,
                 iconUrl: str | None,
                 **kwargs) -> None:
        
        self.userId = userId
        self.name = name
        self.iconUrl = URL(iconUrl) if iconUrl is not None else None

        super().__init__(**kwargs)


class _ProfileItem(APIResponce):
    def __init__(self, id: str,
                 type: str,
                 imageUrl: str,
                 thumbnailUrl: str,
                 **kwargs) -> None:
        
        self.id = id
        self.type = type
        self.imageUrl = URL(imageUrl)
        self.thumbnailUrl = URL(thumbnailUrl)

        super().__init__(**kwargs)


class _Cover(APIResponce):
    def __init__(self, type: str,
                 url: str,
                 **kwargs) -> None:
        self.type = safe_enum(type, pfenum.CoverType)
        self.url = URL(url)
        super().__init__(**kwargs)

        if type not in ['cover_image', 'post_image']:
            warnings.warn(f'Undefined type of "Cover.type": {type}')


class _PostItem(APIResponce):
    def __init__(self, id: str,
                 title: str,
                 feeRequired: int,
                 publishedDatetime: str,
                 updatedDatetime: str,
                 tags: list[str],
                 isLiked: bool,
                 likeCount: int,
                 commentCount: int,
                 isRestricted: bool,
                 user: dict,
                 creatorId: str,
                 hasAdultContent: bool,
                 cover: dict | None,
                 excerpt: str,
                 **kwargs) -> None:

        self.id = id
        self.title = title
        self.feeRequired = feeRequired
        self.publishedDatetime = ISODateTime(publishedDatetime)
        self.updatedDatetime = ISODateTime(updatedDatetime)
        self.tags = tags
        self.isLiked = isLiked
        self.likeCount = likeCount
        self.commentCount = commentCount
        self.isRestricted = isRestricted
        self.user = setclass(user, _User)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.cover = setclass(cover, _Cover)
        self.excerpt = excerpt

        super().__init__(**kwargs)


class _Image(APIResponce):
    def __init__(self, id: str,
                 extension: str,
                 width: int,
                 height: int,
                 originalUrl: str,
                 thumbnailUrl: str,
                 **kwargs) -> None:
        
        self.id = id
        self.extension = extension
        self.width = width
        self.height = height
        self.originalUrl = URL(originalUrl)
        self.thumbnailUrl = URL(thumbnailUrl)

        super().__init__(**kwargs)


class _File(APIResponce):
    def __init__(self, id: str,
                 name: str,
                 extension: str,
                 size: int,
                 url: str,
                 **kwargs) -> None:
        
        self.id = id
        self.name = name
        self.extension = extension
        self.size = size
        self.url = URL(url)

        super().__init__(**kwargs)


class _ArticleParagraphStyle(APIResponce):
    def __init__(self, type: str,
                 offset: int,
                 length: int,
                 **kwargs) -> None:
        
        self.type = safe_enum(type, pfenum.ArticleParagraphStyle)
        self.offset = offset
        self.length = length

        super().__init__(**kwargs)


class _ArticleParagraphLink(APIResponce):
    def __init__(self, offset: int,
                 length: int,
                 url: str,
                 **kwargs) -> None:
        
        self.offset = offset
        self.length = length
        self.url = URL(url)

        super().__init__(**kwargs)


class _ArticleParagraphBlock(APIResponce):
    def __init__(self, type: Literal['p'],
                 text: str,
                 links: list[dict] | Type[UNDEFINED] = UNDEFINED,
                 styles: list[dict] | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:

        self.type = safe_enum(type, pfenum.ArticleBlockType)
        self.text = text
        self.links = maplist(links, _ArticleParagraphLink)
        self.styles = maplist(styles, _ArticleParagraphStyle)

        super().__init__(**kwargs)


class _ArticleHeaderBlock(APIResponce):
    def __init__(self, type: Literal['header'],
                 text: str,
                 **kwargs) -> None:

        self.type = safe_enum(type, pfenum.ArticleBlockType)
        self.text = text

        super().__init__(**kwargs)


class _ArticleImageBlock(APIResponce):
    def __init__(self, type: Literal['image'],
                 imageId: str,
                 **kwargs) -> None:

        self.type = safe_enum(type, pfenum.ArticleBlockType)
        self.imageId = imageId

        super().__init__(**kwargs)


class _ArticleFileBlock(APIResponce):
    def __init__(self, type: Literal['file'],
                 fileId: str,
                 **kwargs) -> None:

        self.type = safe_enum(type, pfenum.ArticleBlockType)
        self.fileId = fileId

        super().__init__(**kwargs)


class _ArticleURLEmbedBlock(APIResponce):
    def __init__(self, type: Literal['url_embed'],
                 urlEmbedId: str,
                 **kwargs) -> None:

        self.type = safe_enum(type, pfenum.ArticleBlockType)
        self.urlEmbedId = urlEmbedId

        super().__init__(**kwargs)


class _UrlEmbed(APIResponce):
    def __init__(self, id: str,
                 type: str,
                 **kwargs) -> None:
        
        self.id = id
        self.type = type

        super().__init__(**kwargs)


class _UrlEmbedDefault(_UrlEmbed):
    def __init__(self, id: str, type: str,
                 host: str,
                 url: str,
                 **kwargs) -> None:
        self.host = host
        self.url = url
        super().__init__(id, type, **kwargs)


class _UrlEmbedHtml(_UrlEmbed):
    def __init__(self, id: str, type: str,
                 html: str,
                 **kwargs) -> None:
        self.html = html
        super().__init__(id, type, **kwargs)


class _UrlEmbedHtmlCard(_UrlEmbedHtml):
    pass


class _UrlEmbedFanboxCreator(_UrlEmbed):
    def __init__(self, id: str, type: str,
                 profile: dict,
                 **kwargs) -> None:
        self.profile = _Creator(**profile)
        super().__init__(id, type, **kwargs)


class _UrlEmbedFanboxPost(_UrlEmbed):
    def __init__(self, id: str, type: str,
                 postInfo: dict,
                 **kwargs) -> None:
        self.postInfo = _EmbedPostInfo(**postInfo)
        super().__init__(id, type, **kwargs)


class _PostInfoBody(APIResponce):
    def __init__(self, text: str | Type[UNDEFINED] = UNDEFINED,
                 files: list[dict] | Type[UNDEFINED] = UNDEFINED,
                 images: list[dict] | Type[UNDEFINED] = UNDEFINED,
                 blocks: list[dict] | Type[UNDEFINED] = UNDEFINED,
                 imageMap: dict[str, dict] | Type[UNDEFINED] = UNDEFINED,
                 fileMap: dict[str, dict] | Type[UNDEFINED] = UNDEFINED,
                 embedMap: dict | Type[UNDEFINED] = UNDEFINED,
                 urlEmbedMap: dict[str, dict] | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:
                
        self.text = text
        self.files = maplist(files, _File)
        self.images = maplist(images, _Image)

        self.blocks = self.map_article_blocks(blocks)
        self.imageMap = mapdict(imageMap, _Image)
        self.fileMap = mapdict(fileMap, _File)
        self.embedMap = embedMap
        self.urlEmbedMap = self.map_url_embeds(urlEmbedMap)
        super().__init__(**kwargs)
    
    @classmethod
    def create_article_block(cls, __dict: dict[Any, Any]):
        _type = __dict['type']
        if _type == 'p':
            return _ArticleParagraphBlock(**__dict)
        elif _type == 'header':
            return _ArticleHeaderBlock(**__dict)
        elif _type == 'image':
            return _ArticleImageBlock(**__dict)
        elif _type == 'file':
            return _ArticleFileBlock(**__dict)
        elif _type == 'url_embed':
            return _ArticleURLEmbedBlock(**__dict)
    
    @classmethod
    def map_article_blocks(
            cls, blocks: list[dict[str, Any]] | Type[UNDEFINED]):
        if isinstance(blocks, type):
            return UNDEFINED
        else:
            return list(map(cls.create_article_block, blocks))
    
    @classmethod
    def create_url_embed(cls, __dict: dict[Any, Any]):
        _type = __dict['type']
        if _type == 'default':
            return _UrlEmbedDefault(**__dict)
        elif _type == 'html':
            return _UrlEmbedHtml(**__dict)
        elif _type == 'html.card':
            return _UrlEmbedHtmlCard(**__dict)
        elif _type == 'fanbox.creator':
            return _UrlEmbedFanboxCreator(**__dict)
        elif _type == 'fanbox.post':
            return _UrlEmbedFanboxPost(**__dict)
    
    @classmethod
    def map_url_embeds(
            cls, __dict: dict[str, dict[str, Any]] | Type[UNDEFINED]):
        if isinstance(__dict, type):
            return UNDEFINED
        else:
            return {k: cls.create_url_embed(v) for k, v in __dict.items()}


class _CommentItem(APIResponce):
    def __init__(self, id: str,
                 parentCommentId: str,
                 rootCommentId: str,
                 body: str,
                 createdDatetime: str,
                 likeCount: int,
                 isLiked: bool,
                 isOwn: bool,
                 user: dict,
                 replies: list[dict] | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:
                 
        self.id = id
        self.parentCommentId = parentCommentId
        self.rootCommentId = rootCommentId
        self.body = body
        self.createdDatetime = ISODateTime(createdDatetime)
        self.likeCount = likeCount
        self.isLiked = isLiked
        self.isOwn = isOwn
        self.user = setclass(user, _User)
        self.replies = maplist(replies, _CommentItem)

        super().__init__(**kwargs)


class _CommentList(APIResponce):
    def __init__(self, items: list, nextUrl: str | None, **kwargs) -> None:
        self.items = items
        self.nextUrl = URL(nextUrl) if nextUrl is not None else None
        super().__init__(**kwargs)


class _ShortPostInfo(APIResponce):
    def __init__(self, id: str,
                 title: str,
                 publishedDatetime: str,
                 **kwargs) -> None:

        self.id = id
        self.title = title
        self.publishedDatetime = ISODateTime(publishedDatetime)

        super().__init__(**kwargs)


class _Payment_Creator(APIResponce):
    def __init__(self, user: dict,
                 creatorId: str,
                 isActive: bool,
                 **kwargs) -> None:

        self.user = setclass(user, _User)
        self.creatorId = creatorId
        self.isActive = isActive
        super().__init__(**kwargs)


# === API Body ===

class _PostListCreator(APIResponce):
    def __init__(self, items: list[dict], nextUrl: str, **kwargs) -> None:
        self.items = maplist(items, _PostItem)
        self.nextUrl = URL(nextUrl)
        super().__init__(**kwargs)


class _PostInfo(APIResponce):
    def __init__(self, id: str,
                 title: str,
                 feeRequired: int,
                 publishedDatetime: str,
                 updatedDatetime: str,
                 type: str,
                 coverImageUrl: str | None,
                 body: dict | None,
                 tags: list[str],
                 isLiked: bool,
                 likeCount: int,
                 commentCount: int,
                 isRestricted: bool,
                 user: dict,
                 creatorId: str,
                 hasAdultContent: bool,
                 commentList: dict,
                 nextPost: dict | None,
                 prevPost: dict | None,
                 imageForShare: str,
                 restrictedFor: int | Type[UNDEFINED] = UNDEFINED,
                 excerpt: str | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:
        
        self.id = id
        self.title = title
        self.coverImageUrl = URL(coverImageUrl) if coverImageUrl is not None else None
        self.feeRequired = feeRequired
        self.publishedDatetime = ISODateTime(publishedDatetime)
        self.updatedDatetime = ISODateTime(updatedDatetime)
        self.type = safe_enum(type, pfenum.PostType)
        self.body = setclass(body, _PostInfoBody)
        self.tags = tags
        self.excerpt = safe_enum(excerpt, pfenum.PostExcerpt)
        self.isLiked = isLiked
        self.likeCount = likeCount
        self.commentCount = commentCount
        self.restrictedFor = safe_enum(restrictedFor, pfenum.PostRestrictedFor)
        self.isRestricted = isRestricted
        self.user = setclass(user, _User)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.commentList = setclass(commentList, _CommentList)
        self.nextPost = setclass(nextPost, _ShortPostInfo)
        self.prevPost = setclass(prevPost, _ShortPostInfo)
        self.imageForShare = imageForShare

        super().__init__(**kwargs)


class _EmbedPostInfo(APIResponce):
    def __init__(self, id: str,
                 title: str,
                 feeRequired: int,
                 publishedDatetime: str,
                 updatedDatetime: str,
                 tags: list[str],
                 isLiked: bool,
                 likeCount: int,
                 commentCount: int,
                 isRestricted: bool,
                 user: dict,
                 creatorId: str,
                 hasAdultContent: bool,
                 restrictedFor: int | Type[UNDEFINED] = UNDEFINED,
                 excerpt: str | Type[UNDEFINED] = UNDEFINED,
                 cover: dict | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:
        
        self.id = id
        self.title = title
        self.feeRequired = feeRequired
        self.publishedDatetime = ISODateTime(publishedDatetime)
        self.updatedDatetime = ISODateTime(updatedDatetime)
        self.tags = tags
        self.excerpt = safe_enum(excerpt, pfenum.PostExcerpt)
        self.isLiked = isLiked
        self.likeCount = likeCount
        self.commentCount = commentCount
        self.restrictedFor = safe_enum(restrictedFor, pfenum.PostRestrictedFor)
        self.isRestricted = isRestricted
        self.user = setclass(user, _User)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.cover = cover

        super().__init__(**kwargs)


class _Plan(APIResponce):
    def __init__(self, id: str,
                 title: str,
                 fee: int,
                 description: str,
                 coverImageUrl: str,
                 user: dict,
                 creatorId: str,
                 hasAdultContent: bool,
                 paymentMethod: str,
                 **kwargs) -> None:
        
        self.id = id
        self.title = title
        self.fee = fee
        self.description = description
        self.coverImageUrl = URL(coverImageUrl)
        self.user = setclass(user, _User)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.paymentMethod = paymentMethod

        super().__init__(**kwargs)


class _Creator(APIResponce):
    def __init__(self, user: dict,
                 creatorId: str,
                 description: str,
                 hasAdultContent: bool,
                 coverImageUrl: str | None,
                 profileLinks: list[str],
                 profileItems: list[dict],
                 isFollowed: bool,
                 isSupported: bool,
                 isStopped: bool,
                 isAcceptingRequest: bool,
                 hasBoothShop: bool,
                 **kwargs) -> None:
        
        self.user = setclass(user, _User)
        self.creatorId = creatorId
        self.description = description
        self.hasAdultContent = hasAdultContent
        self.coverImageUrl = coverImageUrl
        self.profileLinks = profileLinks
        self.profileItems = maplist(profileItems, _ProfileItem)
        self.isFollowed = isFollowed
        self.isSupported = isSupported
        self.isStopped = isStopped
        self.isAcceptingRequest = isAcceptingRequest
        self.hasBoothShop = hasBoothShop
                 
        super().__init__(**kwargs)


class _Tag(APIResponce):
    def __init__(self, tag: str,
                 count: int,
                 coverImageUrl: str,
                 **kwargs) -> None:
        
        self.tag = tag
        self.count = count
        self.coverImageUrl = URL(coverImageUrl)

        super().__init__(**kwargs)


class _BellCountUnreadBody(APIResponce):
    def __init__(self, count: int,
                 **kwargs) -> None:
        
        self.count = count

        super().__init__(**kwargs)


class _Payment(APIResponce):
    def __init__(self, id: str,
                 creator: dict,
                 paidAmount: int,
                 paymentMethod: str,
                 paymentDatetime: str,
                 **kwargs) -> None:
        
        self.id = id
        self.creator = setclass(creator, _Payment_Creator)
        self.paidAmount = paidAmount
        self.paymentMethod = safe_enum(paymentMethod, pfenum.PaymentMethod)
        self.paymentDatetime = ISODateTime(paymentDatetime)

        super().__init__(**kwargs)


# === API Post Responce Types ===

class APIPostPaginate(APIResponce):
    def __init__(self, body: list[str], **kwargs) -> None:
        self.body = list(map(lambda x: URL(x), body))
        super().__init__(**kwargs)


class APIPostListCreator(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = setclass(body, _PostListCreator)
        super().__init__(**kwargs)


class APIPostInfo(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = setclass(body, _PostInfo)
        super().__init__(**kwargs)


class APIPostListComments(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = setclass(body, _CommentList)
        super().__init__(**kwargs)


# === API Creator Responce Types ===

class APICreatorGet(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = setclass(body, _Creator)
        super().__init__(**kwargs)


class APICreatorList(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = maplist(body, _Creator)
        super().__init__(**kwargs)


# === API Plan Responce Types ===

class APIPlanList(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = maplist(body, _Plan)
        super().__init__(**kwargs)


# === API Tag Responce Types ===

class APITagGetFeatured(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = maplist(body, _Tag)
        super().__init__(**kwargs)


# === API Bell Responce Types ===


class APIBellCountUnread(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = setclass(body, _BellCountUnreadBody)
        super().__init__(**kwargs)


# === API User Responce Types ===

class APIUserCountUnreadMessages(APIResponce):
    def __init__(self, body: int, **kwargs) -> None:
        self.body = body
        super().__init__(**kwargs)


# === API Newsletter Responce Types ===

class APINewsletterCountUnread(APIResponce):
    def __init__(self, body: int, **kwargs) -> None:
        self.body = body
        super().__init__(**kwargs)


# === API Payment Responce Types ===

class APIPaymentList(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = maplist(body, _Payment)
        super().__init__(**kwargs)