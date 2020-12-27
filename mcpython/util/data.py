import simplejson


def bytes_to_json(data: bytes):
    return simplejson.loads(data.decode("utf-8"))


def json_to_bytes(data: dict) -> bytes:
    return simplejson.dumps(data, indent="  ").encode("utf-8")
