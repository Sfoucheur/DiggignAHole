import logging
import pyautogui
import time
import random
import os
import keyboard
from typing import List
import numpy as np
from scipy import interpolate
import math
from tkinter import filedialog
from screeninfo import get_monitors
from ui import Ui
import shutil
from PIL import Image  # Import PIL for image handling
import threading  # Import threading
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

pyautogui.MINIMUM_DURATION = 0
pyautogui.MINIMUM_SLEEP = 0
pyautogui.PAUSE = 0


def point_dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def moveBezier(center_x, center_y):
    OFFSET_RANGE = main_ui.click_randomness_var.get()
    center_x += random.randint(-OFFSET_RANGE, OFFSET_RANGE)
    center_y += random.randint(-OFFSET_RANGE, OFFSET_RANGE)
    cp = random.randint(3, 5)
    x1, y1 = pyautogui.position()
    x = np.linspace(x1, center_x, num=cp, dtype='int')
    y = np.linspace(y1, center_y, num=cp, dtype='int')
    RND = 30
    xr = [random.randint(-RND, RND) for _ in range(cp)]
    yr = [random.randint(-RND, RND) for _ in range(cp)]
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    x += xr
    y += yr
    degree = min(3, cp - 1)
    tck, u = interpolate.splprep([x, y], k=degree)
    u_fine = np.linspace(
        0, 1, num=2 + int(point_dist(x1, y1, center_x, center_y) / 50.0))
    points = interpolate.splev(u_fine, tck)
    duration = main_ui.move_duration_var.get() / 10
    timeout = duration / len(points[0])
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
                image=img, region=screen_region, confidence=threshold, grayscale=grayscale)

            if location:
                left, top, width, height = location
                center_x = left + width / 2
                center_y = top + height / 2
                moveBezier(center_x, center_y)
                pyautogui.click()

                # Extract and log image name
                image_name = os.path.splitext(
                    os.path.basename(img.filename))[0]
                logging.info(f"Clicked on {center_x}, {
                             center_y} for {image_name.capitalize()}")

                return True

        except pyautogui.ImageNotFoundException:
            continue  # Proceed to the next image if the current one is not found

        except Exception as error:
            logging.error(
                f"An exception occurred while processing image: {error}")
            # Continue processing the next image

    if running:
        logging.info("No collectable found!")
    return False


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        if os.path.isfile(img_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            # Open the image and append the PIL Image object to the list
            images.append(Image.open(img_path))
    return images


def add_images():
    global image_paths
    target_folder = './images/ores'

    # Ensure the target folder exists
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    file_paths = filedialog.askopenfilenames(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if file_paths:
        for file_path in file_paths:
            # Define the target path
            filename = os.path.basename(file_path)
            target_path = os.path.join(target_folder, filename)

            # Check if the file already exists in the target folder
            if not os.path.exists(target_path):
                # Copy the file to the target folder
                shutil.copy(file_path, target_path)
                # Load the image and add it to the image_paths list
                image_paths.append(Image.open(target_path))
                logging.info(f"Added image: {target_path}")
            else:
                logging.info(f"Image already exists: {target_path}")


def stop_script():
    global running
    if running:
        running = False
        main_ui.status_label.config(text="Status: Stopped")
        logging.info('Stopped script!')


def start_script():
    global running
    if not running:
        running = True
        main_ui.status_label.config(text="Status: Running")
        logging.info('Started script!')
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
    global image_paths
    try:
        screen_index = main_ui.getScreenVar()  # Get the selected screen index
        screen_region = get_screen_region(screen_index)
        interval = main_ui.sleep_duration_var.get()

        while running:
            find_and_click(image_paths, screen_region)
            time.sleep(interval / 1000.0)  # Convert milliseconds to seconds

    except Exception as e:
        logging.error(f'Exception occurred test: {e}', exc_info=True)
        raise


# Initialize UI
main_ui = Ui(start_script, stop_script, add_images)

if __name__ == '__main__':
    logging.info("Starting the application")
    images_folder = './images/ores'
    image_paths = load_images_from_folder(images_folder)
    keyboard.add_hotkey('F7', start_script)
    keyboard.add_hotkey('F8', stop_script)
    keyboard.add_hotkey('ctrl+alt+c', main_ui.exit_script)
    logging.info("Press 'F7' to start the script.")
    logging.info("Press 'F8' to pause the script.")
    logging.info("Press 'Ctrl+alt+c' to stop the script.")
    main_ui.root.mainloop()
