from enum import Enum


class CoverType(str, Enum):
    COVER_IMAGE = 'cover_image'
    POST_IMAGE = 'post_image'


class ArticleParagraphStyle(str, Enum):
    BOLD = 'bold'


class ArticleBlockType(str, Enum):
    P = 'p'
    HEADER = 'header'
    IMAGE = 'image'
    FILE = 'file'
    URL_EMBED = 'url_embed'


class PostType(str, Enum):
    FILE = 'file'


class PostRestrictedFor(int, Enum):
    pass


class PostExcerpt(str, Enum):
    pass


class PaymentMethod(str, Enum):
    PAYPAL = 'paypal'