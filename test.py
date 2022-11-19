import json
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any

import pyfanbox


def _testout(data: str | bytes | dict[Any, Any] | pyfanbox.types.APIResponce):
    filename = 'log/' + datetime.now().isoformat().replace(':', '-')
    if isinstance(data, dict) or isinstance(data, pyfanbox.types.APIResponce):
        with open(filename + '.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False,
                      cls=pyfanbox.FanboxJSONEncoder)
    else:
        try:
            data = json.loads(data)
            with open(filename + '.json', 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except json.decoder.JSONDecodeError:
            with open(filename + '.txt', 'w') as f:
                f.write(data)  # type: ignore


class fanbox_getter(pyfanbox.CC_FANBOX_API):
    def get_current_supportings(self):
        current_supportings: list[pyfanbox.types._Payment_Creator] = []

        payments = self.PAYMENT.listPaid()
        now = datetime.now(timezone(timedelta(hours=9)))
        for p in payments.body:
            payDT = datetime.fromisoformat(p.paymentDatetime)
            if payDT.year == now.year and payDT.month == now.month:
                current_supportings.append(p.creator)
        
        return current_supportings

    def get_available_contents(self, userId):
        available_contents: list[pyfanbox.types._PostItem] = []
        
        urls = self.POST.paginateCreator(userId).body
        for url in urls:
            postList = self.POST.listCreator(**self.parse_qs(url)).body.items
            for post in postList:
                if not post.isRestricted:
                    available_contents.append(post)
        
        return available_contents
    
    def get_all_contents(self, postId: str | int):
        info = self.POST.info(postId).body
        _testout(info)


def main():
    FANBOXSESSID = pyfanbox.auth.get_sessid()
    client = fanbox_getter(FANBOXSESSID)

    current_supportings = client.get_current_supportings()

    for creator in current_supportings:
        posts = client.get_available_contents(creator.creatorId)
        client.get_all_contents()


main()
