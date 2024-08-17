import logging
import subprocess
import pyautogui
import time
import random
import os
import keyboard
from typing import List
import numpy as np
from scipy import interpolate
import math
from screeninfo import get_monitors
from ui import Ui
from PIL import Image  # Import PIL for image handling
import threading  # Import threading
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

# Suppress PIL logging
logging.getLogger("PIL").setLevel(logging.ERROR)

pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0


script_dir = os.getcwd()
relative_images_folder_path = "assets/images"
images_folder_relative = os.path.join(script_dir, relative_images_folder_path)
images_folder = os.path.abspath(images_folder_relative)


def point_dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def moveBezier(center_x, center_y):
    OFFSET_RANGE = main_ui.click_randomness_var.get()
    center_x += random.randint(-OFFSET_RANGE, OFFSET_RANGE)
    center_y += random.randint(-OFFSET_RANGE, OFFSET_RANGE)
    cp = random.randint(6, 15)
    x1, y1 = pyautogui.position()
    x = np.linspace(x1, center_x, num=cp, dtype="int")
    y = np.linspace(y1, center_y, num=cp, dtype="int")
    RND = 30
    xr = [random.randint(-RND, RND) for _ in range(cp)]
    yr = [random.randint(-RND, RND) for _ in range(cp)]
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    x += xr
    y += yr
    degree = min(3, cp - 1)
    tck, u = interpolate.splprep([x, y], k=degree)
    u_fine = np.linspace(
        0, 1, num=2 + int(point_dist(x1, y1, center_x, center_y) / 50.0)
    )
    points = interpolate.splev(u_fine, tck)
    duration = main_ui.move_duration_var.get()
    timeout = duration
    if duration != 0:
        timeout = duration / 1000.0
    point_list = zip(*(i.astype(int) for i in points))
    for point in point_list:
        pyautogui.moveTo(*point)
        time.sleep(timeout)


# TODO parralelize locateOnScreen


def find_and_click(images: List[Image.Image], screen_region):
    global thread
    global running
    threshold = main_ui.detection_threshold_var.get() / 100
    grayscale = main_ui.gray_scale_enabled.get()

    for img in images:
        if not running:
            return False
        try:
            location = pyautogui.locateOnScreen(
                image=img,
                region=screen_region,
                confidence=threshold,
                grayscale=grayscale,
            )

            if location:
                left, top, width, height = location
                center_x = left + width / 2
                center_y = top + height / 2
                moveBezier(center_x, center_y)
                pyautogui.click()

                # Extract and log image name
                image_name = os.path.splitext(os.path.basename(img.filename))[0]
                logging.info(
                    f"Clicked on {center_x}, {center_y} for {image_name.capitalize()}"
                )

                return True

        except pyautogui.ImageNotFoundException:
            continue  # Proceed to the next image if the current one is not found

        except Exception as error:
            logging.error(f"An exception occurred while processing image: {error}")
            # Continue processing the next image

    if running:
        logging.info("No collectable found!")
    return False


def open_folder():
    # explorer would choke on forward slashes
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "assets", "images")
    path = os.path.normpath(images_folder)
    try:
        if os.path.isdir(path):
            subprocess.Popen(f'explorer "{path}"')
        else:
            logging.error(f"Path not found or is not a directory: {path}")
    except Exception as e:
        logging.error(f"Failed to open folder {path}. Error: {e}")


def stop_script():
    global running
    if running:
        running = False
        main_ui.status_label.config(text="Status: Stopped")
        logging.info("Stopped script!")


def start_script():
    global running
    if not running:
        running = True
        main_ui.status_label.config(text="Status: Running")
        logging.info("Started script!")
        # Start the main function in a new thread
        global thread
        thread = threading.Thread(target=main, daemon=True)
        thread.start()


def get_screen_region(screen_index):
    screens = get_monitors()
    if 0 <= screen_index < len(screens):
        monitor = screens[screen_index]
        return (monitor.x, monitor.y, monitor.width, monitor.height)
    else:
        raise IndexError("Invalid screen index")


running = False
thread = None


def main():
    global running
    try:
        screen_index = main_ui.getScreenVar()  # Get the selected screen index
        screen_region = get_screen_region(screen_index)
        interval = main_ui.sleep_duration_var.get()

        while running:
            find_and_click(main_ui.loaded_images, screen_region)
            time.sleep(interval / 1000.0)  # Convert milliseconds to seconds

    except Exception as e:
        logging.error(f"Exception occurred test: {e}", exc_info=True)
        raise


# Initialize UI
main_ui = Ui(start_script, stop_script, open_folder)

if __name__ == "__main__":
    logging.info("Starting the application")
    keyboard.add_hotkey("F7", start_script)
    keyboard.add_hotkey("F8", stop_script)
    keyboard.add_hotkey("ctrl+alt+c", main_ui.exit_script)
    logging.info("Press 'F7' to start the script.")
    logging.info("Press 'F8' to pause the script.")
    logging.info("Press 'Ctrl+alt+c' to stop the script.")
    main_ui.root.mainloop()
