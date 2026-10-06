import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pcapread import core, samples


class PcapreadTest(unittest.TestCase):
    def test_read_small_file(self):
        data = samples.build("little", "us", 65535, [(1, 2, b"abc")])
        index = core.read(data, core.Counter())
        self.assertEqual(index.unit, "us")

    def test_packet_data(self):
        data = samples.build("little", "us", 65535, [(1, 2, b"abc")])
        index = core.read(data, core.Counter())
        self.assertEqual(index.packet(0, core.Counter()).data, b"abc")

    def test_packet_out_of_range(self):
        data = samples.build("little", "us", 65535, [(1, 2, b"abc")])
        index = core.read(data, core.Counter())
        self.assertIsNone(index.packet(7, core.Counter()))

    def test_snaplen_is_stored(self):
        data = samples.build("little", "us", 4096, [(1, 0, b"a")])
        self.assertEqual(core.read(data, core.Counter()).snaplen, 4096)

    def test_packet_fields(self):
        data = samples.build("little", "us", 65535, [(9, 3, b"abc")])
        index = core.read(data, core.Counter())
        packet = index.packet(0, core.Counter())
        self.assertEqual(packet.ts_sec, 9)
        self.assertEqual(packet.ts_frac, 3)
        self.assertEqual(packet.orig_len, 3)

    def test_counter_counts(self):
        data = samples.build("little", "us", 65535, [(1, 2, b"abc")])
        index = core.read(data, core.Counter())
        counter = core.Counter()
        index.packet(0, counter)
        self.assertGreater(counter.scanned, 0)


if __name__ == "__main__":
    unittest.main()
