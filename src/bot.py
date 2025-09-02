import sys
import time
import logging

from src import constants
from src import screenshot
from src.adb_commands import send_adb_tap, turn_screen_off
from src.adb_checker import check_adb_status, wait_for_device
from src.game_action import GameActions
from src.image_decision_maker import make_decision
from src.image_template_loader import load_image_templates


def run():
    # Check ADB status before starting the bot
    logging.info("Checking ADB status...")
    is_ready, status_message = check_adb_status()
    
    if not is_ready:
        logging.error(f"ADB is not ready: {status_message}")
        logging.info("Waiting for ADB device to become available...")
        
        if not wait_for_device(timeout_seconds=30):
            logging.error("ADB device did not become available within 30 seconds.")
            logging.error("Please ensure:")
            logging.error("1. ADB (Android Debug Bridge) is installed")
            logging.error("2. Your Android device is connected via USB")
            logging.error("3. USB debugging is enabled on your device")
            logging.error("4. You have authorized the USB debugging connection")
            sys.exit(1)
    else:
        logging.info(status_message)

    # Time the bot will stay in game until it forfeits
    time_to_stay_in_game = 5

    # Start the timer until bot forfeits the game
    start_time = time.time()

    template_images = load_image_templates()

    game_entered = False
    waiting_for_device = False

    while True:
        # Capture a screenshot and save it to a file
        if not screenshot.capture_screenshot(constants.SCREENSHOT_FILE_NAME):
            if waiting_for_device:
                print(".", end="", flush=True)
            else:
                logging.info(
                    "Error capturing screenshot. Waiting until phone is connected."
                )
                waiting_for_device = True

            # sys.exit(1)
            time.sleep(5)
            continue

        if waiting_for_device:
            waiting_for_device = False
            # print to jump to the next line after only printing ...... without jumping to next line
            print()

        # Check if the timer has run out
        elapsed_time = time.time() - start_time
        if game_entered and elapsed_time > time_to_stay_in_game:
            logging.info("Timer has run out. Forfeit the game.")
            send_adb_tap(75, 460)
            time.sleep(1)
            send_adb_tap(429, 1254)
            time.sleep(1)

        next_action = make_decision(template_images, constants.SCREENSHOT_FILE_NAME)

        if next_action.action == GameActions.tap_position:
            # If not ingame reset timer
            if next_action.is_ingame:
                if not game_entered:
                    start_time = time.time()
                    game_entered = True
            else:
                start_time = time.time()
                game_entered = False

            send_adb_tap(next_action.position[0], next_action.position[1])

        elif next_action.action == GameActions.exit_program:
            turn_screen_off()
            logging.info("Max number of games played. Exit program.")
            sys.exit()

        time.sleep(2)
