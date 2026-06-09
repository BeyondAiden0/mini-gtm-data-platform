import argparse
from pathlib import Path

import duckdb

from context import getAccountContext
from draft import draftEmail
from resolver import findAccountCandidates


warehousePath = Path(__file__).parent.parent / "warehouse" / "data.duckdb"


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Account name, email, person name, or id")
    return parser.parse_args()


def main():
    args = parseArgs()

    with duckdb.connect(str(warehousePath), read_only=True) as conn:
        candidates = findAccountCandidates(conn, args.query)

        if not candidates:
            return

        context = getAccountContext(conn, candidates[0])

    print(draftEmail(context))


if __name__ == "__main__":
    main()
