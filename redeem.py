import sys
import time
import random

from api import redeem_gift_code
from csv_reader import load_players
from config import MIN_DELAY, MAX_DELAY
from logger import log


def print_summary(counter, total, elapsed, gift_code):
    """Print final redemption summary."""

    minutes, seconds = divmod(int(elapsed), 60)

    log("")
    log("=" * 60)
    log("Redemption Summary")
    log("=" * 60)

    log(f"Gift Code : {gift_code}")
    log(f"Processed : {total}")
    log("")

    log(f"SUCCESS   : {counter['SUCCESS']}", "SUCCESS")
    log(f"RECEIVED  : {counter['RECEIVED']}", "WARNING")
    log(f"FAILED    : {counter['FAILED']}", "ERROR")

    log("")
    log(f"Elapsed   : {minutes}m {seconds}s")
    log("=" * 60)


def main():
    # -------------------------------------------------
    # Command line
    # -------------------------------------------------

    if len(sys.argv) != 2:
        print()
        print("Usage:")
        print("  python redeem.py <gift_code>")
        print()
        print("Example:")
        print("  python redeem.py FB4Million")
        sys.exit(1)

    gift_code = sys.argv[1].strip()

    if not gift_code:
        print("Gift code cannot be empty.")
        sys.exit(1)

    # -------------------------------------------------
    # Load players
    # -------------------------------------------------

    try:
        players = load_players()

    except FileNotFoundError as e:
        log(str(e), "ERROR")
        sys.exit(1)

    except ValueError as e:
        log(str(e), "ERROR")
        sys.exit(1)

    except Exception as e:
        log(f"Failed to load players.csv: {e}", "ERROR")
        sys.exit(1)

    if not players:
        log("No valid players found in data/players.csv.", "ERROR")
        sys.exit(1)

    total = len(players)

    # -------------------------------------------------
    # Start
    # -------------------------------------------------

    log("")
    log("=" * 60)
    log("WOS Gift Code Batch Redeemer")
    log("=" * 60)
    log(f"Gift Code : {gift_code}")
    log(f"Players   : {total}")
    log("=" * 60)
    log("")

    counter = {
        "SUCCESS": 0,
        "RECEIVED": 0,
        "FAILED": 0,
    }

    start_time = time.time()

    # -------------------------------------------------
    # Redemption loop
    # -------------------------------------------------

    try:
        for index, player in enumerate(players, start=1):

            fid = player["fid"]
            kid = player["kid"]
            name = player.get("name", "")

            if name:
                display = f"{name} (FID={fid}, KID={kid})"
            else:
                display = f"FID={fid}, KID={kid}"

            log(f"[{index}/{total}] {display}")

            try:
                result = redeem_gift_code(
                    player=player,
                    cdk=gift_code,
                )

            except Exception as e:
                log(f" -> Unexpected error: {e}", "ERROR")
                counter["FAILED"] += 1

                if index < total:
                    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

                continue

            # API normally returns a dict.
            if not isinstance(result, dict):
                log(f" -> Invalid API response: {result}", "ERROR")
                counter["FAILED"] += 1

            else:
                raw_msg = str(
                    result.get("msg", "UNKNOWN")
                ).strip()

                # API sometimes returns "TIME ERROR."
                msg = raw_msg.rstrip(".").upper()

                if msg in ("SUCCESS", "SAME TYPE EXCHANGE"):
                    counter["SUCCESS"] += 1
                    log(f" -> {msg}", "SUCCESS")

                elif msg == "RECEIVED":
                    counter["RECEIVED"] += 1
                    log(" -> ALREADY RECEIVED", "WARNING")

                else:
                    counter["FAILED"] += 1

                    err_code = result.get("err_code")

                    if err_code is not None:
                        log(
                            f" -> {msg} (err_code={err_code})",
                            "ERROR",
                        )
                    else:
                        log(f" -> {msg}", "ERROR")

                    # Gift code itself is expired.
                    # No point sending it to another 400 players.
                    if msg == "TIME ERROR":
                        log(
                            "Gift code has expired. Stopping.",
                            "WARNING",
                        )
                        break

                    # Global redemption limit reached.
                    if msg == "USED":
                        log(
                            "Gift code claim limit reached. Stopping.",
                            "WARNING",
                        )
                        break

            # Random delay between players.
            # Do not sleep after the final player.
            if index < total:
                time.sleep(
                    random.uniform(
                        MIN_DELAY,
                        MAX_DELAY,
                    )
                )

    except KeyboardInterrupt:
        log("")
        log("Stopped by user.", "WARNING")

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    elapsed = time.time() - start_time

    processed = (
        counter["SUCCESS"]
        + counter["RECEIVED"]
        + counter["FAILED"]
    )

    print_summary(
        counter=counter,
        total=processed,
        elapsed=elapsed,
        gift_code=gift_code,
    )


if __name__ == "__main__":
    main()
