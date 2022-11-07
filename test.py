import json
from datetime import datetime
from typing import Any

import pyfanbox


def _testout(data: str | bytes | dict[Any, Any] | pyfanbox.types.APIResponce):
    filename = 'log\\' + datetime.now().isoformat().replace(':', '-')
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


def main():
    FANBOXSESSID = pyfanbox.auth.get_sessid()
    api = pyfanbox.CC_FANBOX_API(FANBOXSESSID)
    _testout(api.CREATOR.listRelated(4218636))


main()
