import json
import warnings
from typing import Any, Literal, NewType, Type, TypedDict

UNDEFINED = type('UNDEFINED', (object,), {})

URL = NewType('URL', str)
ISODateTime = NewType('ISODateTime', str)


def cvtlist(_l: list[dict] | UNDEFINED | None, type: type) -> list[Any]:
    if _l == UNDEFINED:
        return UNDEFINED  # type: ignore
    else:
        return list(map(lambda x: type(**x), _l))


def cvtdict(_d: dict[str, dict], type: type) -> dict[str, Any]:
    if _d == UNDEFINED:
        return UNDEFINED  # type: ignore
    else:
        return {k: type(**v) for k, v in _d.items()}


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
    def __init__(self, type: Literal['cover_image', 'post_image'],
                 url: str,
                 **kwargs) -> None:
        self.type = type
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
        self.user = _User(**user)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.cover = _Cover(**cover) if cover is not None else None
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
    def __init__(self, type: Literal['bold'],
                 offset: int,
                 length: int,
                 **kwargs) -> None:
        
        self.type = type
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


class _ArticleBlock(APIResponce):
    def __init__(self, type: Literal['p', 'header', 'image', 'file', 'url_embed'],
                 text: str | Type[UNDEFINED] = UNDEFINED,
                 styles: list[dict] | Type[UNDEFINED] = UNDEFINED,
                 imageId: str | Type[UNDEFINED] = UNDEFINED,
                 links: list[dict] | Type[UNDEFINED] = UNDEFINED,
                 fileId: str | Type[UNDEFINED] = UNDEFINED,
                 urlEmbedId: str | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:

        self.type = type
        self.text = text
        self.styles: list[_ArticleParagraphStyle] = cvtlist(styles, _ArticleParagraphStyle)
        self.imageId = imageId
        self.links: list[_ArticleParagraphLink] = cvtlist(links, _ArticleParagraphLink)
        self.fileId = fileId
        self.urlEmbedId = urlEmbedId

        super().__init__(**kwargs)


class _UrlEmbed(APIResponce):
    def __init__(self, id: str,
                 type: str,
                 html: str | Type[UNDEFINED] = UNDEFINED,
                 url: str | Type[UNDEFINED] = UNDEFINED,
                 host: str | Type[UNDEFINED] = UNDEFINED,
                 postInfo: dict | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:
        
        self.id = id
        self.type = type
        self.url = url
        self.host = host
        if type == 'fanbox.post':
            self.postInfo = _EmbedPostInfo(**postInfo)
        else:
            self.html = html

        super().__init__(**kwargs)


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
        self.files: list[_File] = cvtlist(files, _File)
        self.images: list[_Image] = cvtlist(images, _Image)

        self.blocks: list[_ArticleBlock] = cvtlist(blocks, _ArticleBlock)
        self.imageMap: dict[str, _Image] = cvtdict(imageMap, _Image)
        self.fileMap: dict[str, _File] = cvtdict(fileMap, _File)
        self.embedMap = embedMap
        self.urlEmbedMap: dict[str, _UrlEmbed] = cvtdict(urlEmbedMap, _UrlEmbed)
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
        self.user = _User(**user)
        self.replies: list[_CommentItem] = cvtlist(replies, _CommentItem)

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

        self.user = _User(**user)
        self.creatorId = creatorId
        self.isActive = isActive
        super().__init__(**kwargs)


# === API Body ===

class _PostListCreator(APIResponce):
    def __init__(self, items: list[dict], nextUrl: str, **kwargs) -> None:
        self.items: list[_PostItem] = cvtlist(items, _PostItem)
        self.nextUrl = URL(nextUrl)
        super().__init__(**kwargs)


class _PostInfo(APIResponce):
    def __init__(self, id: str,
                 title: str,
                 feeRequired: int,
                 publishedDatetime: str,
                 updatedDatetime: str,
                 type: Literal['file'],
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
                 restrictedFor: Literal[1, 2, 3] | Type[UNDEFINED] = UNDEFINED,
                 excerpt: Literal[''] | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:
        
        self.id = id
        self.title = title
        self.coverImageUrl = URL(coverImageUrl) if coverImageUrl is not None else None
        self.feeRequired = feeRequired
        self.publishedDatetime = ISODateTime(publishedDatetime)
        self.updatedDatetime = ISODateTime(updatedDatetime)
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
                 restrictedFor: Literal[1, 2, 3] | Type[UNDEFINED] = UNDEFINED,
                 excerpt: Literal[''] | Type[UNDEFINED] = UNDEFINED,
                 cover: dict | Type[UNDEFINED] = UNDEFINED,
                 **kwargs) -> None:
        
        self.id = id
        self.title = title
        self.feeRequired = feeRequired
        self.publishedDatetime = ISODateTime(publishedDatetime)
        self.updatedDatetime = ISODateTime(updatedDatetime)
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
        self.coverImageUrl = URL(coverImageUrl)
        self.profileLinks = profileLinks
        self.profileItems: list[_ProfileItem] = cvtlist(profileItems, _ProfileItem)
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
                 paymentMethod: Literal['paypal'],
                 paymentDatetime: str,
                 **kwargs) -> None:
        
        self.id = id
        self.creator = _Payment_Creator(**creator)
        self.paidAmount = paidAmount
        self.paymentMethod = paymentMethod
        self.paymentDatetime = ISODateTime(paymentDatetime)

        super().__init__(**kwargs)


# === API Post Responce Types ===

class APIPostPaginate(APIResponce):
    def __init__(self, body: list[str], **kwargs) -> None:
        self.body = list(map(lambda x: URL(x), body))
        super().__init__(**kwargs)


class APIPostListCreator(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _PostListCreator(**body)
        super().__init__(**kwargs)


class APIPostInfo(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _PostInfo(**body)
        super().__init__(**kwargs)


class APIPostListComments(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _CommentList(**body)
        super().__init__(**kwargs)


# === API Creator Responce Types ===

class APICreatorGet(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _Creator(**body)
        super().__init__(**kwargs)


class APICreatorList(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body: list[_Creator] = cvtlist(body, _Creator)
        super().__init__(**kwargs)


# === API Plan Responce Types ===

class APIPlanList(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body: list[_Plan] = cvtlist(body, _Plan)
        super().__init__(**kwargs)


# === API Tag Responce Types ===

class APITagGetFeatured(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body: list[_Tag] = cvtlist(body, _Tag)
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


# === API Payment Responce Types ===

class APIPaymentList(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body: list[_Payment] = cvtlist(body, _Payment)
        super().__init__(**kwargs)