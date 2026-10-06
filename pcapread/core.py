"""解析全局头与记录头，并按序号取包。"""


_MAGIC = {
    b"\xd4\xc3\xb2\xa1": ("little", "us"),
    b"\xa1\xb2\xc3\xd4": ("big", "us"),
    b"\x4d\x3c\xb2\xa1": ("little", "ns"),
    b"\xa1\xb2\x3c\x4d": ("big", "ns"),
}

_GLOBAL_HEADER = 24
_RECORD_HEADER = 16


class Counter:
    """记录扫描过的记录条数。"""

    def __init__(self):
        self.scanned = 0


class Packet:
    def __init__(self, index, ts_sec, ts_frac, data, orig_len, unit):
        self.index = index
        self.ts_sec = ts_sec
        self.ts_frac = ts_frac
        self.data = data
        self.orig_len = orig_len
        self.unit = unit


class Index:
    def __init__(self):
        self.data = b""
        self.endian = "little"
        self.unit = "us"
        self.snaplen = 0
        self.records = []

    def packet(self, i, counter):
        if not 0 <= i < len(self.records):
            return None
        counter.scanned += 1
        offset, incl = self.records[i]
        data = self.data
        ts_sec = int.from_bytes(data[offset:offset + 4], self.endian)
        ts_frac = int.from_bytes(data[offset + 4:offset + 8], self.endian)
        orig = int.from_bytes(data[offset + 12:offset + 16], self.endian)
        payload = data[offset + _RECORD_HEADER:offset + _RECORD_HEADER + incl]
        return Packet(i, ts_sec, ts_frac, payload, orig, self.unit)


def read(data, counter):
    magic = _MAGIC.get(data[:4])
    if magic is None:
        raise ValueError("bad-magic")
    endian, unit = magic
    index = Index()
    index.data = data
    index.endian = endian
    index.unit = unit
    index.snaplen = int.from_bytes(data[16:20], endian)
    offset = _GLOBAL_HEADER
    total = len(data)
    while offset + _RECORD_HEADER <= total:
        incl = int.from_bytes(data[offset + 8:offset + 12], endian)
        if incl > index.snaplen or offset + _RECORD_HEADER + incl > total:
            break
        index.records.append((offset, incl))
        offset += _RECORD_HEADER + incl
    return index
