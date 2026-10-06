"""解析全局头与记录头，并按序号取包。"""

MAGIC_TABLE = {
    b"\xd4\xc3\xb2\xa1": ("little", "us"),
    b"\xa1\xb2\xc3\xd4": ("big", "us"),
    b"\x4d\x3c\xb2\xa1": ("little", "ns"),
    b"\xa1\xb2\x3c\x4d": ("big", "ns"),
}


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
        offset, ts_sec, ts_frac, orig_len, incl_len = self.records[i]
        payload = self.data[offset + 16:offset + 16 + incl_len]
        return Packet(i, ts_sec, ts_frac, payload, orig_len, self.unit)


def read(data, counter):
    index = Index()
    index.data = data
    spec = MAGIC_TABLE.get(bytes(data[:4]))
    if spec is None:
        raise ValueError("bad-magic")
    endian, unit = spec
    index.endian = endian
    index.unit = unit
    if len(data) < 24:
        raise ValueError("bad-magic")
    index.snaplen = int.from_bytes(data[16:20], endian)

    offset = 24
    while offset + 16 <= len(data):
        counter.scanned += 1
        ts_sec = int.from_bytes(data[offset:offset + 4], endian)
        ts_frac = int.from_bytes(data[offset + 4:offset + 8], endian)
        incl_len = int.from_bytes(data[offset + 8:offset + 12], endian)
        orig_len = int.from_bytes(data[offset + 12:offset + 16], endian)
        if incl_len > index.snaplen:
            break
        if offset + 16 + incl_len > len(data):
            break
        index.records.append((offset, ts_sec, ts_frac, orig_len, incl_len))
        offset += 16 + incl_len
    return index
