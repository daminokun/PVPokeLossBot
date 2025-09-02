import os
import cv2
import numpy as np
import time
from src.find_image_result import FindImageResult

def find_image_fast(screenshot_img, template_img, threshold=0.75, image_file_name="unknown"):
    try:
        result = cv2.matchTemplate(screenshot_img, template_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"[DEBUG] Matching {image_file_name} -> Max match: {max_val:.2f}")

        h, w = template_img.shape[:2]
        center_x, center_y = max_loc[0] + w // 2, max_loc[1] + h // 2

        if max_val >= threshold:
            os.makedirs("debug", exist_ok=True)

            # Generate unique filename
            safe_name = image_file_name.replace("/", "_").replace("\\", "_")
            timestamp = int(time.time() * 1000)
            debug_filename = f"debug/debug_{safe_name}_{timestamp}.png"

            # Draw rectangle and center dot
            debug_img = screenshot_img.copy()
            cv2.rectangle(debug_img, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 255, 0), 2)
            cv2.circle(debug_img, (center_x, center_y), 5, (0, 0, 255), -1)
            cv2.imwrite(debug_filename, debug_img)

            return FindImageResult(
                val=max_val,
                coords=(center_x, center_y),
                template_w=w,
                template_h=h
            )
        else:
            print(f"[DEBUG] No match above threshold. Best match: {max_val:.2f} (template: {image_file_name})")
    except Exception as e:
        print(f"[ERROR] Template matching failed for {image_file_name}: {e}")

    return None
