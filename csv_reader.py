import csv
from pathlib import Path

from logger import log


# -------------------------------------------------
# CSV Configuration
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "players.csv"


def load_players():
    """
    Load players from data/players.csv.

    Required columns:
        fid,kid

    Optional column:
        name

    Example:
        fid,kid,name
        12087362,265,Main
        22156300,273,Farm01
        26666459,281,

    Returns:
        list[dict]

    Example:
        [
            {
                "fid": "12087362",
                "kid": "265",
                "name": "Main"
            }
        ]
    """

    # -------------------------------------------------
    # Check file
    # -------------------------------------------------

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"players.csv not found: {CSV_PATH}"
        )

    if not CSV_PATH.is_file():
        raise FileNotFoundError(
            f"players.csv is not a valid file: {CSV_PATH}"
        )

    players = []
    seen_fids = set()

    invalid_count = 0
    duplicate_count = 0

    # -------------------------------------------------
    # Read CSV
    # -------------------------------------------------

    try:
        with CSV_PATH.open(
            mode="r",
            newline="",
            encoding="utf-8-sig",
        ) as f:

            reader = csv.DictReader(f)

            # Empty CSV
            if reader.fieldnames is None:
                raise ValueError(
                    "players.csv is empty or has no header."
                )

            # Normalize header names
            reader.fieldnames = [
                field.strip().lower()
                for field in reader.fieldnames
                if field is not None
            ]

            required_columns = {"fid", "kid"}

            missing_columns = (
                required_columns - set(reader.fieldnames)
            )

            if missing_columns:
                missing = ", ".join(sorted(missing_columns))

                raise ValueError(
                    f"players.csv is missing required column(s): "
                    f"{missing}"
                )

            # -------------------------------------------------
            # Process rows
            # -------------------------------------------------

            for row_number, row in enumerate(reader, start=2):

                # Ignore completely empty rows
                if not row:
                    continue

                fid = str(row.get("fid") or "").strip()
                kid = str(row.get("kid") or "").strip()
                name = str(row.get("name") or "").strip()

                # Ignore completely blank lines
                if not fid and not kid and not name:
                    continue

                # ---------------------------------------------
                # Validate FID
                # ---------------------------------------------

                if not fid:
                    log(
                        f"Row {row_number}: Missing FID. Skipped.",
                        "WARNING",
                    )
                    invalid_count += 1
                    continue

                if not fid.isdigit():
                    log(
                        f"Row {row_number}: "
                        f"Invalid FID '{fid}'. Skipped.",
                        "WARNING",
                    )
                    invalid_count += 1
                    continue

                # ---------------------------------------------
                # Validate KID
                # ---------------------------------------------

                if not kid:
                    log(
                        f"Row {row_number}: "
                        f"Missing KID for FID {fid}. Skipped.",
                        "WARNING",
                    )
                    invalid_count += 1
                    continue

                if not kid.isdigit():
                    log(
                        f"Row {row_number}: "
                        f"Invalid KID '{kid}' "
                        f"for FID {fid}. Skipped.",
                        "WARNING",
                    )
                    invalid_count += 1
                    continue

                # ---------------------------------------------
                # Duplicate FID
                # ---------------------------------------------

                if fid in seen_fids:
                    log(
                        f"Row {row_number}: "
                        f"Duplicate FID {fid}. Skipped.",
                        "WARNING",
                    )
                    duplicate_count += 1
                    continue

                seen_fids.add(fid)

                # ---------------------------------------------
                # Add player
                # ---------------------------------------------

                players.append(
                    {
                        "fid": fid,
                        "kid": kid,
                        "name": name,
                    }
                )

    except UnicodeDecodeError as e:
        raise ValueError(
            "Unable to read players.csv. "
            "Please save it as UTF-8 CSV."
        ) from e

    except csv.Error as e:
        raise ValueError(
            f"Invalid CSV format: {e}"
        ) from e

    # -------------------------------------------------
    # Final validation
    # -------------------------------------------------

    if not players:
        raise ValueError(
            "No valid players found in players.csv."
        )

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    log(f"Loaded {len(players)} valid player(s).")

    if duplicate_count:
        log(
            f"Ignored {duplicate_count} duplicate FID(s).",
            "WARNING",
        )

    if invalid_count:
        log(
            f"Ignored {invalid_count} invalid row(s).",
            "WARNING",
        )

    return players
