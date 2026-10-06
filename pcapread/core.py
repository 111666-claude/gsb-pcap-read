"""解析全局头与记录头，并按序号取包。"""


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
        self.unit = "us"
        self.snaplen = 0
        self.records = []

    def packet(self, i, counter):
        offset = 24
        n = 0
        while offset + 16 <= len(self.data):
            counter.scanned += 1
            incl = int.from_bytes(self.data[offset + 8:offset + 12], "little")
            if n == i:
                ts_sec = int.from_bytes(self.data[offset:offset + 4], "little")
                ts_frac = int.from_bytes(self.data[offset + 4:offset + 8], "little")
                orig = int.from_bytes(self.data[offset + 12:offset + 16], "little")
                payload = self.data[offset + 16:offset + 16 + incl]
                return Packet(i, ts_sec, ts_frac, payload, orig, self.unit)
            offset += 16 + incl
            n += 1
        return None


def read(data, counter):
    index = Index()
    index.data = data
    if data[:4] != b"\xd4\xc3\xb2\xa1":
        raise ValueError("bad-magic")
    index.snaplen = int.from_bytes(data[16:20], "little")
    return index
