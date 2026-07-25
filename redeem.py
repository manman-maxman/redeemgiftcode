import csv
import sys
import time
from pathlib import Path

from api import redeem_gift_code
from logger import log


def load_players(csv_path: Path):
    """
    Read players.csv

    Supported formats:
        fid,kid
        fid,kid,name
    """

    players = []
    seen = set()

    with open(csv_path, newline="", encoding="utf-8-sig") as f:

        reader = csv.DictReader(f)

        required = {"fid", "kid"}

        if not required.issubset(reader.fieldnames):
            raise ValueError("players.csv must contain 'fid' and 'kid' columns.")

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

            players.append({
                "fid": fid,
                "kid": kid,
                "name": name,
            })

    return players


def print_summary(counter, elapsed):

    log("")
    log("=" * 60)
    log("Finished")
    log("")

    log(f"SUCCESS  : {counter['SUCCESS']}")
    log(f"RECEIVED : {counter['RECEIVED']}")
    log(f"FAILED   : {counter['FAILED']}")

    log("")
    log(f"Elapsed : {elapsed:.1f} sec")
    log("=" * 60)


def main():

    if len(sys.argv) != 2:

        print("Usage:")
        print("python redeem.py FB4Million")
        sys.exit(1)

    gift_code = sys.argv[1]

    csv_file = Path("data/players.csv")

    if not csv_file.exists():

        print("players.csv not found.")
        sys.exit(1)

    players = load_players(csv_file)

    log(f"Loaded {len(players)} players.")
    log("")

    counter = {
        "SUCCESS": 0,
        "RECEIVED": 0,
        "FAILED": 0,
    }

    start = time.time()

    total = len(players)

    for index, player in enumerate(players, start=1):

        display_name = player["name"] or player["fid"]

        log(
            f"[{index}/{total}] "
            f"{display_name} "
            f"(FID={player['fid']}, KID={player['kid']})"
        )

        result = redeem_gift_code(
            player=player,
            cdk=gift_code,
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
