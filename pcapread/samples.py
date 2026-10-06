"""固定场景，用来复现题面里的锚点。"""

import json

from . import core

MAGICS = {
    ("little", "us"): b"\xd4\xc3\xb2\xa1",
    ("big", "us"): b"\xa1\xb2\xc3\xd4",
    ("little", "ns"): b"\x4d\x3c\xb2\xa1",
    ("big", "ns"): b"\xa1\xb2\x3c\x4d",
}


def _line(obj):
    print(json.dumps(obj, ensure_ascii=False))


def build(endian, unit, snaplen, records):
    out = bytearray()
    out += MAGICS[(endian, unit)]
    out += (2).to_bytes(2, endian) + (4).to_bytes(2, endian)
    out += (0).to_bytes(4, endian) + (0).to_bytes(4, endian)
    out += snaplen.to_bytes(4, endian)
    out += (1).to_bytes(4, endian)
    for sec, frac, payload in records:
        out += sec.to_bytes(4, endian) + frac.to_bytes(4, endian)
        out += len(payload).to_bytes(4, endian) + len(payload).to_bytes(4, endian)
        out += payload
    return bytes(out)


def count_packets(index, counter):
    n = 0
    while index.packet(n, counter) is not None:
        n += 1
    return n


def run(name):
    if name == "be":
        data = build("big", "us", 65535, [(1, 2, b"abc")])
        index = core.read(data, core.Counter())
        _line({"unit": index.unit, "ts_sec": index.packet(0, core.Counter()).ts_sec})
        return 0
    if name == "nano":
        data = build("little", "ns", 65535, [(1, 500, b"abc")])
        index = core.read(data, core.Counter())
        _line({"unit": index.unit})
        return 0
    if name == "snaplen":
        data = build("little", "us", 64, [(1, 0, b"x" * 100)])
        index = core.read(data, core.Counter())
        _line({"packets": count_packets(index, core.Counter())})
        return 0
    if name == "trunc":
        full = build("little", "us", 1000, [(1, 0, b"y" * 200)])
        data = full[:24 + 16 + 50]
        index = core.read(data, core.Counter())
        _line({"packets": count_packets(index, core.Counter())})
        return 0
    if name == "work":
        records = [(i, 0, b"\x01\x02\x03\x04") for i in range(2000)]
        data = build("little", "us", 65535, records)
        index = core.read(data, core.Counter())
        counter = core.Counter()
        for i in range(2000):
            index.packet(i, counter)
        _line({"packets": 2000, "scanned": counter.scanned})
        return 0
    raise SystemExit("未知场景：" + name)
