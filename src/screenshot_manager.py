import os
import glob

def get_screenshot_files(directory, pattern="screenshot*.png"):
    """Return a list of screenshot files sorted by creation time."""
    files = glob.glob(os.path.join(directory, pattern))
    return sorted(files, key=os.path.getctime)

def limit_screenshots(directory, max_count=5):
    """Delete oldest screenshots if there are more than max_count in the directory."""
    screenshots = get_screenshot_files(directory)
    while len(screenshots) >= max_count:
        os.remove(screenshots[0])
        screenshots.pop(0)

def next_screenshot_filename(directory):
    """Determine the next screenshot filename based on existing files."""
    screenshots = get_screenshot_files(directory)
    if screenshots:
        nums = []
        for f in screenshots:
            base = os.path.basename(f)
            num_str = base.replace("screenshot", "").replace(".png", "")
            if num_str.isdigit():
                nums.append(int(num_str))
        next_num = max(nums) + 1 if nums else 1
    else:
        next_num = 1
    return os.path.join(directory, f"screenshot{next_num}.png")

def save_new_screenshot():
    """Limit screenshots to 5 and save a new screenshot as screenshotN.png in current directory."""
    directory = os.getcwd()
    limit_screenshots(directory, max_count=5)
    new_filename = next_screenshot_filename(directory)
    # Use adb to pull screenshot from device to current directory
    os.system('adb shell screencap -p /sdcard/screenshot.png')
    os.system(f'adb pull /sdcard/screenshot.png "{new_filename}"')
    os.system('adb shell rm /sdcard/screenshot.png')
    print(f"Saved screenshot: {new_filename}")

# Usage:
# Call save_new_screenshot() whenever you want to save a screenshot
