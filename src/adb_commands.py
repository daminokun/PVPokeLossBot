import os
import logging

# Optional: configure logging (you can move this to your main script if needed)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
)


def send_adb_tap(x: int, y: int) -> bool:
    """
    Simulates a tap on the screen at the given coordinates using ADB.

    Args:
        x (int): The x-coordinate.
        y (int): The y-coordinate.

    Returns:
        bool: True if the command was successful, False otherwise.
    """
    adb_command = f"adb shell input tap {x} {y}"
    logging.info(f"Sending ADB tap to ({x}, {y})")
    error_code = os.system(adb_command)

    if error_code == 0:
        logging.info("ADB tap succeeded.")
    else:
        logging.error(f"ADB tap failed with error code {error_code}.")

    return error_code == 0


def turn_screen_off() -> bool:
    """
    Simulates the power button (toggles screen on/off) using ADB.

    Returns:
        bool: True if the command was successful, False otherwise.
    """
    adb_command = "adb shell input keyevent 26"
    logging.info("Sending ADB keyevent 26 (power button toggle)")
    error_code = os.system(adb_command)

    if error_code == 0:
        logging.info("Screen toggle succeeded.")
    else:
        logging.error(f"Screen toggle failed with error code {error_code}.")

    return error_code == 0
