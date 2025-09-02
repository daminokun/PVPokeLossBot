import os
import platform


import subprocess
import logging

def capture_screenshot(filename: str) -> bool:
    try:
       # Run ADB command to take a screenshot and capture output
        result = subprocess.run(
            ['adb', 'exec-out', 'screencap', '-p'],
            capture_output=True,
            timeout=10
        )

        if result.returncode != 0:
            logging.error(f"ADB screencap failed: {result.stderr.decode().strip()}")
            return False

        # Save screenshot to file
        with open(filename, 'wb') as f:
            f.write(result.stdout)

        logging.debug(f"Screenshot saved to: {filename}")
        return True

    except subprocess.TimeoutExpired:
        logging.error("ADB command timed out while capturing screenshot.")
        return False

    except Exception as e:
        logging.error(f"Unexpected error capturing screenshot: {e}")
        return False
