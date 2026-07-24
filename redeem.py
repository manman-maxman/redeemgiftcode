import csv
import sys
import time
from pathlib import Path

from api import redeem_gift_code
from logger import log


def load_accounts(csv_path: str):
    """
    Read accounts.csv

    Support:

    fid,kid
    fid,kid,name
    """

    accounts = []
    seen = set()

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if "fid" not in reader.fieldnames or "kid" not in reader.fieldnames:
            raise ValueError("CSV must contain fid and kid columns.")

        for row in reader:

            fid = row["fid"].strip()
            kid = row["kid"].strip()
            name = row.get("name", "").strip()

            if not fid.isdigit():
                continue

            if not kid.isdigit():
                continue

            if fid in seen:
                continue

            seen.add(fid)

            accounts.append({
                "fid": fid,
                "kid": kid,
                "name": name
            })

    return accounts


def print_summary(result_counter, elapsed):

    log("")
    log("=" * 60)

    log("Finished")

    log(f"SUCCESS  : {result_counter.get('SUCCESS',0)}")
    log(f"RECEIVED : {result_counter.get('RECEIVED',0)}")
    log(f"FAILED   : {result_counter.get('FAILED',0)}")

    log("")
    log(f"Elapsed : {elapsed:.1f} sec")

    log("=" * 60)


def main():

    if len(sys.argv) != 2:

        print()

        print("Usage:")
        print("python redeem.py FB4Million")

        sys.exit(1)

    gift_code = sys.argv[1]

    csv_file = Path("data/accounts.csv")

    if not csv_file.exists():

        print("accounts.csv not found.")

        sys.exit(1)

    accounts = load_accounts(csv_file)

    log(f"Loaded {len(accounts)} accounts.")
    log("")

    counter = {
        "SUCCESS": 0,
        "RECEIVED": 0,
        "FAILED": 0
    }

    start = time.time()

    total = len(accounts)

    for index, account in enumerate(accounts, start=1):

        fid = account["fid"]
        kid = account["kid"]
        name = account["name"]

        display = name if name else fid

        log(f"[{index}/{total}] {display}")

        result = redeem_gift_code(
            fid=fid,
            kid=kid,
            cdk=gift_code
        )

        msg = result.get("msg", "FAILED").replace(".", "")

        log(f" -> {msg}")

        if msg == "SUCCESS":
            counter["SUCCESS"] += 1

        elif msg == "RECEIVED":
            counter["RECEIVED"] += 1

        else:
            counter["FAILED"] += 1

        time.sleep(1)

    elapsed = time.time() - start

    print_summary(counter, elapsed)


if __name__ == "__main__":
    main()
