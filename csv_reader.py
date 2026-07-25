import csv
from pathlib import Path

from logger import error, info, warning


CSV_PATH = Path("data/players.csv")


def load_accounts():
    """
    Read accounts from data/accounts.csv

    Returns:
        list[dict]
    """

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Cannot find {CSV_PATH}")

    accounts = []
    seen = set()

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:

        reader = csv.DictReader(f)

        required = {"fid", "kid"}

        if not required.issubset(reader.fieldnames):
            raise ValueError(
                "accounts.csv must contain columns: fid,kid"
            )

        for row_number, row in enumerate(reader, start=2):

            fid = row["fid"].strip()
            kid = row["kid"].strip()
            name = row.get("name", "").strip()

            if not fid.isdigit():
                warning(f"Row {row_number}: Invalid FID -> {fid}")
                continue

            if not kid.isdigit():
                warning(f"Row {row_number}: Invalid KID -> {kid}")
                continue

            if fid in seen:
                warning(f"Duplicate FID ignored -> {fid}")
                continue

            seen.add(fid)

            accounts.append({
                "fid": fid,
                "kid": kid,
                "name": name
            })

    info(f"Loaded {len(accounts)} account(s).")

    return accounts
