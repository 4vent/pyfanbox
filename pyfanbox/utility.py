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
