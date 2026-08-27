# -------------------------------------------------
# WOS Gift Code API
# -------------------------------------------------

BASE_URL = "https://wos-giftcode-api.centurygame.com"

REDEEM_URL = f"{BASE_URL}/api/gift_code"

WOS_ENCRYPT_KEY = "tB87#kPtkxqOS2"


# -------------------------------------------------
# HTTP / Retry Settings
# -------------------------------------------------

REQUEST_TIMEOUT = 15

MAX_RETRIES = 3

RETRY_DELAY = 2


# -------------------------------------------------
# Delay Between Players
# -------------------------------------------------

MIN_DELAY = 0.8

MAX_DELAY = 1.3


# -------------------------------------------------
# Browser Header Settings
# -------------------------------------------------

CHROME_MIN_VERSION = 148

CHROME_MAX_VERSION = 150


# -------------------------------------------------
# Result Messages
# -------------------------------------------------

SUCCESS_MESSAGES = {
    "SUCCESS",
    "SAME TYPE EXCHANGE",
}

ALREADY_REDEEMED_MESSAGES = {
    "RECEIVED",
}

STOP_MESSAGES = {
    "TIME ERROR",
    "USED",
}


# -------------------------------------------------
# Retryable HTTP Status Codes
# -------------------------------------------------

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}
