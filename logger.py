from datetime import datetime
from colorama import Fore, Style, init

# Enable ANSI color on Windows
init(autoreset=True)


LEVEL_COLOR = {
    "INFO": Fore.CYAN,
    "SUCCESS": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "DEBUG": Fore.MAGENTA,
}


def log(message: str, level: str = "INFO") -> None:
    """
    Print timestamped log message.

    Example:
        log("Loaded 478 accounts")
        log("Redeemed successfully", "SUCCESS")
        log("Network timeout", "WARNING")
        log("Invalid sign", "ERROR")
    """

    level = level.upper()

    color = LEVEL_COLOR.get(level, Fore.WHITE)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(
        f"{color}[{timestamp}] "
        f"[{level}] "
        f"{message}"
        f"{Style.RESET_ALL}"
    )
