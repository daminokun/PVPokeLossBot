import sys
import time
import logging
import hashlib

from src import constants
from src import screenshot
from src.adb_commands import send_adb_tap, turn_screen_off
from src.game_action import GameActions
from src.image_decision_maker import make_decision
from src.image_template_loader import load_image_templates

last_hash = None

def hash_image(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def run():
    time_to_stay_in_game = 3
    start_time = time.time()
    template_images = load_image_templates()

    game_entered = False
    waiting_for_device = False

    while True:
        # Capture screenshot
        if not screenshot.capture_screenshot(constants.SCREENSHOT_FILE_NAME):
            if waiting_for_device:
                print(".", end="", flush=True)
            else:
                logging.info("Error capturing screenshot. Waiting until phone is connected.")
                waiting_for_device = True
            time.sleep(5)
            continue

        if waiting_for_device:
            waiting_for_device = False
            print()

        # ✅ Frame-skip: skip processing if screenshot hasn't changed
        global last_hash
        new_hash = hash_image(constants.SCREENSHOT_FILE_NAME)
        if new_hash == last_hash:
            time.sleep(2.5)  # match normal sleep to avoid high CPU
            continue
        last_hash = new_hash

        # Timer check
        elapsed_time = time.time() - start_time
        if game_entered and elapsed_time > time_to_stay_in_game:
            logging.info("Timer has run out. Looking for forfeit button.")

            forfeit_action = make_decision(template_images, constants.SCREENSHOT_FILE_NAME)

            if (
                forfeit_action
                and forfeit_action.action == GameActions.tap_position
                and forfeit_action.is_ingame
                and 380 < forfeit_action.position[1] < 960  # Only tap if in upper half
            ):
                logging.info(f"Tapping forfeit button at {forfeit_action.position}")
                send_adb_tap(*forfeit_action.position)
                time.sleep(1)
            else:
                logging.warning("Forfeit button not found in upper half of screen. Skipping first tap.")

            # Always send second tap regardless
            send_adb_tap(429, 1254)
            time.sleep(1)

        # Image match decision
        next_action = make_decision(template_images, constants.SCREENSHOT_FILE_NAME)

        if next_action and next_action.action == GameActions.tap_position:
            if next_action.is_ingame:
                if not game_entered:
                    start_time = time.time()
                    game_entered = True
            else:
                start_time = time.time()
                game_entered = False

            send_adb_tap(next_action.position[0], next_action.position[1])

        elif next_action and next_action.action == GameActions.exit_program:
            turn_screen_off()
            logging.info("Max number of games played. Exit program.")
            sys.exit()

        # ✅ Main loop sleep (slower cycle = lower CPU)
        time.sleep(1.5)
