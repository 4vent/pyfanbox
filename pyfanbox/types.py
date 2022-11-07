import json
import warnings
from typing import Any, Literal, TypedDict


class Cookie(TypedDict):
    domain: str
    expiry: int
    httpOnly: bool
    name: str
    path: str
    secure: bool
    value: str


class UNDEFINED():
    pass


class APIResponce():
    def __init__(self, **kwargs) -> None:
        for k, v in kwargs:
            warnings.warn('Unknown Key found. (Module bug or Updated Fanbox API.)\n'
                          'You can use this key but there is no autocomplete.')
            setattr(self, k, v)


class FanboxJSONEncoder(json.encoder.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, APIResponce):
            return {k: v for k, v in o.__dict__.items()
                    if k not in [] or not v == UNDEFINED}
        else:
            return super().default(o)


class _User(APIResponce):
    def __init__(self, userId: str,
                 name: str,
                 iconUrl: str,
                 **kwargs) -> None:
        
        self.userId = userId
        self.name = name
        self.iconUrl = iconUrl

        super().__init__(**kwargs)


class _ProfileItem(APIResponce):
    def __init__(self, id: str,
                 type: str,
                 imageUrl: str,
                 thumbnailUrl: str,
                 **kwargs) -> None:
        
        self.id = id
        self.type = type
        self.imageUrl = imageUrl
        self.thumbnailUrl = thumbnailUrl

        super().__init__(**kwargs)


class APIPostPaginate(APIResponce):
    def __init__(self, body: list[str], **kwargs) -> None:
        self.body = body
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
        self.coverImageUrl = coverImageUrl
        self.profileLinks = profileLinks
        self.profileItems = list(map(lambda x: _ProfileItem(**x), profileItems))
        self.isFollowed = isFollowed
        self.isSupported = isSupported
        self.isStopped = isStopped
        self.isAcceptingRequest = isAcceptingRequest
        self.hasBoothShop = hasBoothShop
                 
        super().__init__(**kwargs)


class APICreatorGet(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _Creator(**body)
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
        self.coverImageUrl = coverImageUrl
        self.user = _User(**user)
        self.creatorId = creatorId
        self.hasAdultContent = hasAdultContent
        self.paymentMethod = paymentMethod

        super().__init__(**kwargs)


class APIPlanListCreator(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = list(map(lambda x: _Plan(**x), body))
        super().__init__(**kwargs)


class _Tag(APIResponce):
    def __init__(self, tag: str,
                 count: int,
                 coverImageUrl: str,
                 **kwargs) -> None:
        
        self.tag = tag
        self.count = count
        self.coverImageUrl = coverImageUrl

        super().__init__(**kwargs)


class APITagGetFeatured(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = list(map(lambda x: _Tag(**x), body))
        super().__init__(**kwargs)


class _BellCountUnreadBody(APIResponce):
    def __init__(self, count: int,
                 **kwargs) -> None:
        
        self.count = count

        super().__init__(**kwargs)


class APIBellCountUnread(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _BellCountUnreadBody(**body)
        super().__init__(**kwargs)


class APICountUnreadMessages(APIResponce):
    def __init__(self, body: int, **kwargs) -> None:
        self.body = body
        super().__init__(**kwargs)


class APINewsletterCountUnread(APIResponce):
    def __init__(self, body: int, **kwargs) -> None:
        self.body = body
        super().__init__(**kwargs)


class APICreatorListRecommended(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = list(map(lambda x: _Creator(**x), body))
        super().__init__(**kwargs)


class _Cover(APIResponce):
    def __init__(self, type: Literal['cover_image'],
                 url: str,
                 **kwargs) -> None:
        self.type = type
        self.url = url
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
        self.publishedDatetime = publishedDatetime
        self.updatedDatetime = updatedDatetime
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


class _PostListCreator(APIResponce):
    def __init__(self, items: list[dict], nextUrl: str, **kwargs) -> None:
        self.items = list(map(lambda x: _PostItem(**x), items))
        self.nextUrl = nextUrl
        super().__init__(**kwargs)


class APIPostListCreator(APIResponce):
    def __init__(self, body: dict, **kwargs) -> None:
        self.body = _PostListCreator(**body)
        super().__init__(**kwargs)


class APICreatorListRelated(APIResponce):
    def __init__(self, body: list[dict], **kwargs) -> None:
        self.body = list(map(lambda x: _Creator(**x), body))
        super().__init__(**kwargs)