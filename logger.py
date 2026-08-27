from datetime import datetime

try:
    import colorama
    from colorama import Fore, Style

    colorama.init(autoreset=True)

    COLORS = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
    }

    RESET = Style.RESET_ALL
    DIM = Style.DIM

except ImportError:
    COLORS = {
        "INFO": "",
        "SUCCESS": "",
        "WARNING": "",
        "ERROR": "",
    }

    RESET = ""
    DIM = ""


def log(message="", level="INFO"):
    """
    Print a timestamped log message.

    Supported levels:
        INFO
        SUCCESS
        WARNING
        ERROR

    Examples:
        log("Starting...")
        log("Redeemed successfully", "SUCCESS")
        log("Rate limited", "WARNING")
        log("Request failed", "ERROR")
    """

    level = str(level).upper()

    if level not in COLORS:
        level = "INFO"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    color = COLORS[level]

    output = (
        f"{DIM}{timestamp}{RESET}"
        f" - "
        f"{color}{message}{RESET}"
    )

    try:
        print(output, flush=True)

    except UnicodeEncodeError:
        # Fallback for terminals with poor Unicode support
        safe_output = (
            output
            .encode("ascii", errors="replace")
            .decode("ascii")
        )

        print(safe_output, flush=True)
