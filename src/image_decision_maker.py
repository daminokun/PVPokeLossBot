import logging
import cv2
import os
from concurrent.futures import ThreadPoolExecutor

from src import constants, image_service
from src.find_image_result import FindImageResult
from src.game_action import GameAction, GameActions


def is_ingame(image_file: str) -> bool:
    return image_file.startswith("ingame_") or image_file == "enemy_charge_attack.png"


def is_screen_to_attack(image_file: str) -> bool:
    return image_file.startswith("ingame_")


def make_decision(template_images: dict[str, cv2.Mat], image_name: str) -> GameAction:
    if not os.path.exists(image_name):
        logging.error(f"Missing image: {image_name}")
        raise FileNotFoundError(f"Screenshot file not found: {image_name}")

    img_screenshot = cv2.imread(image_name, cv2.IMREAD_COLOR)
    if img_screenshot is None:
        logging.error(f"Failed to load screenshot: {image_name}")
        raise ValueError("Screenshot is None — check image path or format")

    logging.debug(f"Screenshot loaded: {image_name}, shape: {img_screenshot.shape}")
    logging.debug(f"Submitting {len(template_images)} template comparisons...")

    find_image_results = []

    def compare_image(image_file, img_template):
        threshold = 0.77
        if image_file.startswith("forfeit"):
            threshold = 0.70

        try:
            result = image_service.find_image_fast(
                img_screenshot, img_template, threshold, image_file
            )
        except Exception as e:
            logging.error(f"Error in find_image_fast for {image_file}: {e}")
            return None

        if result and result.val >= threshold:
            if image_file.startswith("forfeit"):
                x, y = result.coords
                if not (380 < y < 800):
                    logging.debug(f"Skipped forfeit match at {x},{y} — outside valid Y range.")
                    return None
            logging.debug(f"Match: {image_file} @ {result.val:.2f} (threshold: {threshold})")
            return (image_file, result)

        return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(compare_image, file, tmpl)
            for file, tmpl in template_images.items()
        ]
        for future in futures:
            try:
                match = future.result(timeout=10)  # Prevent hanging
                if match:
                    find_image_results.append(match)
            except Exception as e:
                logging.error(f"Error in image matching thread: {e}")

    logging.debug(f"Total matches: {len(find_image_results)}")
    return analyze_results_and_return_action_with_priority(find_image_results)


def analyze_results_and_return_action_with_priority(find_image_results: list[tuple[str, FindImageResult]]) -> GameAction:
    if not find_image_results:
        return GameAction(action=None)  # no-op

    priority_list = [
        "max_number_of_games_played_text",
        "claim_",
        "reward_",
        "start_button_text",
        "select_master",
        "select_great",
        "select_hypa",
        "vs",
        "forfeit",
    ]

    for priority_file in priority_list:
        for image_file, result in find_image_results:
            if image_file.startswith(priority_file):
                action = analyze_results_and_return_action(image_file, result)
                if action and hasattr(action, "action") and action.action:
                    return action

    # ✅ NEW fallback logic below this line
    for image_file, result in sorted(find_image_results, key=lambda x: x[1].val, reverse=True):
        action = analyze_results_and_return_action(image_file, result)
        if action and action.action:
            logging.info(f"Falling back to: {image_file} with confidence {result.val:.2f}")
            return action

    logging.warning("No valid matches found even after fallback.")
    return GameAction(action=None)


def analyze_results_and_return_action(image_file: str, result: FindImageResult) -> GameAction:
    logging.info(f"Selected: {image_file} ({result.val * 100:.2f}%)")

    if image_file.startswith("forfeit"):
        x, y = result.coords
        if not (380 < y < 800):
            logging.warning(f"Rejected forfeit match at Y={y} (must be between 381 and 799)")
            return GameAction(action=None)

    if image_file.startswith("max_number_of_games_played_text"):
        return GameAction(action=GameActions.exit_program)

    if is_ingame(image_file):
        tap_pos = constants.ATTACK_TAP_POSITION if is_screen_to_attack(image_file) else result.coords
        return GameAction(action=GameActions.tap_position, position=tap_pos, is_ingame=True)

    return GameAction(action=GameActions.tap_position, position=result.coords)
