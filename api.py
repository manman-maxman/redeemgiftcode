import hashlib
import random
import time

import requests

from config import (
    REDEEM_URL,
    WOS_ENCRYPT_KEY,
    MAX_RETRIES,
    RETRY_DELAY,
)

from logger import log


# ---------------------------------------------------
# Sign
# ---------------------------------------------------

def encode_data(data: dict) -> dict:
    """
    Generate request signature.

    sign = md5(sorted_query + secret)
    """

    sorted_keys = sorted(data.keys())

    encoded = "&".join(
        f"{key}={data[key]}"
        for key in sorted_keys
    )

    sign = hashlib.md5(
        f"{encoded}{WOS_ENCRYPT_KEY}".encode("utf-8")
    ).hexdigest()

    return {
        "sign": sign,
        **data
    }


# ---------------------------------------------------
# HTTP
# ---------------------------------------------------

def make_request(payload: dict):

    version = random.randint(148, 150)

    headers = {

        "User-Agent":
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{version}.0.0.0 Safari/537.36",

        "Accept":
        "application/json, text/plain, */*",

        "Content-Type":
        "application/x-www-form-urlencoded",

        "Origin":
        "https://wos-giftcode.centurygame.com",

        "Referer":
        "https://wos-giftcode.centurygame.com/",

        "sec-ch-ua":
        f"\"Not;A=Brand\";v=\"8\", "
        f"\"Chromium\";v=\"{version}\", "
        f"\"Google Chrome\";v=\"{version}\"",

        "sec-ch-ua-mobile":
        "?0",

        "sec-ch-ua-platform":
        "\"Windows\"",

        "sec-fetch-mode":
        "cors",

        "sec-fetch-site":
        "same-site",

        "sec-fetch-dest":
        "empty",
    }

    for attempt in range(MAX_RETRIES):

        try:

            response = requests.post(
                REDEEM_URL,
                headers=headers,
                data=payload,
                timeout=15
            )

            if response.status_code == 200:
                return response.json()

            log(
                f"HTTP {response.status_code} "
                f"(Attempt {attempt+1}/{MAX_RETRIES})"
            )

        except requests.RequestException as e:

            log(
                f"Network Error "
                f"(Attempt {attempt+1}/{MAX_RETRIES}) "
                f"{e}"
            )

        time.sleep(RETRY_DELAY)

    return {
        "code": -1,
        "msg": "REQUEST FAILED"
    }


# ---------------------------------------------------
# Redeem
# ---------------------------------------------------

def redeem_gift_code(fid: str,
                     kid: str,
                     cdk: str):

    payload = {

        "fid": fid,
        "kid": kid,
        "cdk": cdk,
        "time": int(time.time())
    }

    payload = encode_data(payload)

    return make_request(payload)
