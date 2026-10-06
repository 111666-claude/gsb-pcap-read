"""命令行入口。"""

import argparse
import json

from . import core, samples


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pcapread")
    ap.add_argument("--sample", choices=["be", "nano", "snaplen", "trunc", "work"])
    args = ap.parse_args(argv)
    if args.sample:
        try:
            return samples.run(args.sample)
        except ValueError as exc:
            print(json.dumps({"error": str(exc)}))
            return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
