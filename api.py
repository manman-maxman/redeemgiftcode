import hashlib
import random
import time

import requests

from config import (
    REDEEM_URL,
    WOS_ENCRYPT_KEY,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    CHROME_MIN_VERSION,
    CHROME_MAX_VERSION,
    RETRYABLE_STATUS_CODES,
)

from logger import log


# -------------------------------------------------
# Shared HTTP Session
# -------------------------------------------------

_session = requests.Session()


# -------------------------------------------------
# Signature
# -------------------------------------------------

def encode_data(data: dict) -> dict:
    """
    Generate request signature.

    Official format currently observed:

        cdk=<code>&fid=<fid>&kid=<kid>&time=<unix_time><secret>

    Keys are sorted alphabetically before hashing.
    """

    sorted_keys = sorted(data.keys())

    encoded_data = "&".join(
        f"{key}={data[key]}"
        for key in sorted_keys
    )

    sign_source = f"{encoded_data}{WOS_ENCRYPT_KEY}"

    sign = hashlib.md5(
        sign_source.encode("utf-8")
    ).hexdigest()

    return {
        "sign": sign,
        **data,
    }


# -------------------------------------------------
# Headers
# -------------------------------------------------

def build_headers() -> dict:
    """
    Build browser-like request headers.

    Chrome version is randomized slightly to avoid
    sending an identical fingerprint every request.
    """

    version = random.randint(
        CHROME_MIN_VERSION,
        CHROME_MAX_VERSION,
    )

    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            f"Chrome/{version}.0.0.0 Safari/537.36"
        ),

        "Accept":
            "application/json, text/plain, */*",

        "Accept-Encoding":
            "gzip, deflate, br, zstd",

        "Accept-Language":
            "en-US,en;q=0.9",

        "Content-Type":
            "application/x-www-form-urlencoded",

        "Origin":
            "https://wos-giftcode.centurygame.com",

        "Referer":
            "https://wos-giftcode.centurygame.com/",

        "sec-ch-ua": (
            f'"Not;A=Brand";v="8", '
            f'"Chromium";v="{version}", '
            f'"Google Chrome";v="{version}"'
        ),

        "sec-ch-ua-mobile":
            "?0",

        "sec-ch-ua-platform":
            '"Windows"',

        "sec-fetch-dest":
            "empty",

        "sec-fetch-mode":
            "cors",

        "sec-fetch-site":
            "same-site",
    }


# -------------------------------------------------
# HTTP Request
# -------------------------------------------------

def make_request(payload: dict) -> dict:
    """
    POST payload to the official gift code API.

    Automatically retries temporary/network failures.

    Returns:
        dict
    """

    headers = build_headers()

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            response = _session.post(
                REDEEM_URL,
                data=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )

        except requests.exceptions.Timeout:

            log(
                f"Request timeout "
                f"(attempt {attempt}/{MAX_RETRIES})",
                "WARNING",
            )

        except requests.exceptions.ConnectionError as e:

            log(
                f"Connection error "
                f"(attempt {attempt}/{MAX_RETRIES}): {e}",
                "WARNING",
            )

        except requests.exceptions.RequestException as e:

            log(
                f"Request error "
                f"(attempt {attempt}/{MAX_RETRIES}): {e}",
                "ERROR",
            )

        else:

            # -----------------------------------------
            # HTTP 200
            # -----------------------------------------

            if response.status_code == 200:

                try:
                    result = response.json()

                except ValueError:

                    log(
                        "Server returned HTTP 200 "
                        "but response was not valid JSON.",
                        "ERROR",
                    )

                    return {
                        "code": -1,
                        "msg": "INVALID JSON RESPONSE",
                    }

                if not isinstance(result, dict):

                    log(
                        f"Unexpected API response: {result}",
                        "ERROR",
                    )

                    return {
                        "code": -1,
                        "msg": "INVALID API RESPONSE",
                    }

                return result

            # -----------------------------------------
            # Retryable HTTP error
            # -----------------------------------------

            if response.status_code in RETRYABLE_STATUS_CODES:

                body = response.text[:200]

                log(
                    f"HTTP {response.status_code} "
                    f"(attempt {attempt}/{MAX_RETRIES}) "
                    f"{body}",
                    "WARNING",
                )

            # -----------------------------------------
            # Non-retryable HTTP error
            # -----------------------------------------

            else:

                body = response.text[:300]

                log(
                    f"HTTP {response.status_code}: {body}",
                    "ERROR",
                )

                return {
                    "code": -1,
                    "msg": f"HTTP {response.status_code}",
                }

        # ---------------------------------------------
        # Retry delay
        # ---------------------------------------------

        if attempt < MAX_RETRIES:

            # Give HTTP 429 a slightly longer pause.
            delay = RETRY_DELAY

            try:
                if (
                    "response" in locals()
                    and response.status_code == 429
                ):
                    delay *= 2
            except Exception:
                pass

            time.sleep(delay)

    return {
        "code": -1,
        "msg": "REQUEST FAILED",
    }


# -------------------------------------------------
# Gift Code Redemption
# -------------------------------------------------

def redeem_gift_code(player: dict, cdk: str) -> dict:
    """
    Redeem one gift code for one player.

    player format:

        {
            "fid": "12087362",
            "kid": "265",
            "name": "Main"
        }

    Current official API payload:

        fid
        kid
        cdk
        time
        sign
    """

    fid = str(
        player.get("fid", "")
    ).strip()

    kid = str(
        player.get("kid", "")
    ).strip()

    # -------------------------------------------------
    # Basic validation
    # -------------------------------------------------

    if not fid.isdigit():

        return {
            "code": -1,
            "msg": "INVALID FID",
        }

    if not kid.isdigit():

        return {
            "code": -1,
            "msg": "INVALID KID",
        }

    if not cdk or not cdk.strip():

        return {
            "code": -1,
            "msg": "EMPTY GIFT CODE",
        }

    # -------------------------------------------------
    # New API uses Unix seconds, not milliseconds
    # -------------------------------------------------

    payload = {
        "fid": fid,
        "cdk": cdk.strip(),
        "kid": kid,
        "time": int(time.time()),
    }

    signed_payload = encode_data(payload)

    return make_request(signed_payload)
