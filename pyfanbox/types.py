import json
import warnings
from typing import Any, Literal, NewType, TypedDict


class Cookie(TypedDict):
    domain: str
    expiry: int
    httpOnly: bool
    name: str
    path: str
    secure: bool
    value: str


UNDEFINED = type('UNDEFINED', (object,), {})

Uri = NewType('Uri', str)
ISOTime = NewType('ISOTime', str)


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
            warnings.warn(f'Unknown Key "{k}" found. (Module bug or Updated Fanbox API.) '
                          'You can use this key but there is no autocomplete.')
            setattr(self, k, v)


# === API Body Element ===

class _User(APIResponce):
    def __init__(self, userId: str,
                 name: str,
                 iconUrl: str,
                 **kwargs) -> None:
        
        self.userId = userId
        self.name = name
        self.iconUrl = Uri(iconUrl)

        super().__init__(**kwargs)


class _ProfileItem(APIResponce):
    def __init__(self, id: str,
                 type: str,
                 imageUrl: str,
                 thumbnailUrl: str,
                 **kwargs) -> None:
        
        self.id = id
        self.type = type
        self.imageUrl = Uri(imageUrl)
        self.thumbnailUrl = Uri(thumbnailUrl)

        super().__init__(**kwargs)


class _Cover(APIResponce):
    def __init__(self, type: Literal['cover_image'],
                 url: str,
                 **kwargs) -> None:
        self.type = type
        self.url = Uri(url)
        super().__init__(**kwargs)

        if type not in ['cover_image']:
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
        self.publishedDatetime = ISOTime(publishedDatetime)
        self.updatedDatetime = ISOTime(updatedDatetime)
        self.tags = tags
        self.isLiked = isLiked
        self.likeCount = likeCount
        self.commentCount = commentCount
        self.isRestricted = isRestricted
        self.user = _User(**user)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.cover = _Cover(**cover) if cover is not None else None
        self.excerpt = excerpt

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
        self.url = Uri(url)

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
        self.originalUrl = Uri(originalUrl)
        self.thumbnailUrl = Uri(thumbnailUrl)

        super().__init__(**kwargs)


class _PostInfoBody(APIResponce):
    def __init__(self, text: str = UNDEFINED,  # type: ignore
                 files: list[dict] = UNDEFINED,  # type: ignore
                 images: list[dict] = UNDEFINED,  # type: ignore
                 **kwargs) -> None:
        self.text = text
        self.files = list(map(lambda x: _File(**x), files)) if files is not UNDEFINED else UNDEFINED
        self.images = list(map(lambda x: _Image(**x), images)) if images is not UNDEFINED else UNDEFINED
        super().__init__(**kwargs)


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
                 replies: list[dict] = UNDEFINED,  # type: ignore
                 **kwargs) -> None:
                 
        self.id = id
        self.parentCommentId = parentCommentId
        self.rootCommentId = rootCommentId
        self.body = body
        self.createdDatetime = ISOTime(createdDatetime)
        self.likeCount = likeCount
        self.isLiked = isLiked
        self.isOwn = isOwn
        self.user = _User(**user)
        self.replies = (list(map(lambda x: _CommentItem(**x), replies))
                        if replies is not UNDEFINED else UNDEFINED)

        super().__init__(**kwargs)


class _CommentList(APIResponce):
    def __init__(self, items: list, nextUrl: str, **kwargs) -> None:
        self.items = items
        self.nextUrl = Uri(nextUrl)
        super().__init__(**kwargs)


class _ShortPostInfo(APIResponce):
    def __init__(self, id: str,
                 title: str,
                 publishedDatetime: str,
                 **kwargs) -> None:

        self.id = id
        self.title = title
        self.publishedDatetime = ISOTime(publishedDatetime)

        super().__init__(**kwargs)


# === API Body ===

class _PostListCreator(APIResponce):
    def __init__(self, items: list[dict], nextUrl: str, **kwargs) -> None:
        self.items = list(map(lambda x: _PostItem(**x), items))
        self.nextUrl = Uri(nextUrl)
        super().__init__(**kwargs)


class _PostInfo(APIResponce):
    def __init__(self, id: str,
                 title: str,
                 feeRequired: int,
                 publishedDatetime: str,
                 updatedDatetime: str,
                 type: Literal['file'],
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
                 restrictedFor: Literal[1, 2, 3] = UNDEFINED,  # type: ignore
                 coverImageUrl: str = UNDEFINED,  # type: ignore
                 excerpt: Literal[''] = UNDEFINED,  # type: ignore
                 **kwargs) -> None:
        
        self.id = id
        self.title = title
        self.coverImageUrl = Uri(coverImageUrl)
        self.feeRequired = feeRequired
        self.publishedDatetime = ISOTime(publishedDatetime)
        self.updatedDatetime = ISOTime(updatedDatetime)
        self.type = type
        self.body = _PostInfoBody(**body) if body is not None else None
        self.tags = tags
        self.excerpt = excerpt
        self.isLiked = isLiked
        self.likeCount = likeCount
        self.commentCount = commentCount
        self.restrictedFor = restrictedFor
        self.isRestricted = isRestricted
        self.user = _User(**user)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.commentList = _CommentList(**commentList)
        self.nextPost = _ShortPostInfo(**nextPost) if nextPost is not None else None
        self.prevPost = _ShortPostInfo(**prevPost) if prevPost is not None else None
        self.imageForShare = imageForShare

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
        self.coverImageUrl = Uri(coverImageUrl)
        self.user = _User(**user)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.paymentMethod = paymentMethod

        super().__init__(**kwargs)


class _Creator(APIResponce):
    def __init__(self, user: dict,
                 creatorId: str,
                 description: str,
                 hasAdultContent: bool,
                 coverImageUrl: str,
                 profileLinks: list[str],
                 profileItems: list[dict],
                 isFollowed: bool,
                 isSupported: bool,
                 isStopped: bool,
                 isAcceptingRequest: bool,
                 hasBoothShop: bool,
                 **kwargs) -> None:
        
        self.user = _User(**user)
        self.creatorId = creatorId
        self.description = description
        self.hasAdultContent = hasAdultContent
        self.coverImageUrl = Uri(coverImageUrl)
        self.profileLinks = profileLinks
        self.profileItems = list(map(lambda x: _ProfileItem(**x), profileItems))
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
        self.coverImageUrl = Uri(coverImageUrl)

        super().__init__(**kwargs)


class _BellCountUnreadBody(APIResponce):
    def __init__(self, count: int,
                 **kwargs) -> None:
        
        self.count = count

        super().__init__(**kwargs)


# === API Post Responce Types ===

class APIPostPaginate(APIResponce):
    def __init__(self, body: list[str], **kwargs) -> None:
        self.body = body
        super().__init__(**kwargs)


class APIPostListCreator(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _PostListCreator(**body)
        super().__init__(**kwargs)


class APIPostInfo(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _PostInfo(**body)
        super().__init__(**kwargs)


# === API Creator Responce Types ===

class APICreatorGet(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _Creator(**body)
        super().__init__(**kwargs)


class APICreatorListRecommended(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = list(map(lambda x: _Creator(**x), body))
        super().__init__(**kwargs)


class APICreatorListRelated(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = list(map(lambda x: _Creator(**x), body))
        super().__init__(**kwargs)


# === API Plan Responce Types ===

class APIPlanListCreator(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = list(map(lambda x: _Plan(**x), body))
        super().__init__(**kwargs)


# === API Tag Responce Types ===

class APITagGetFeatured(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = list(map(lambda x: _Tag(**x), body))
        super().__init__(**kwargs)


# === API Bell Responce Types ===


class APIBellCountUnread(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _BellCountUnreadBody(**body)
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