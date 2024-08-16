# main_window.py

import tkinter as tk
import logging
import json
import os
import re
from screeninfo import get_monitors
from config_window import ConfigWindow
from PIL import Image
from select_window import FolderSelectorApp
import pyautogui


script_dir = os.getcwd()
relative_config_folder_path = "assets/config.json"
config_path_relative = os.path.join(script_dir, relative_config_folder_path)
config_path = os.path.abspath(config_path_relative)

relative_images_folder_path = "assets/images"
images_folder_relative = os.path.join(script_dir, relative_images_folder_path)
images_folder = os.path.abspath(images_folder_relative)


class TkinterLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        try:
            msg = self.format(record)
            self.text_widget.configure(state=tk.NORMAL)
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.yview(tk.END)  # Scroll to the end
            self.text_widget.configure(state=tk.DISABLED)
        except Exception:
            self.handleError(record)


class Ui:
    root = tk.Tk()
    colour1 = "#020f12"  # Window background color
    colour2 = "#05d7ff"
    colour3 = "#65e7ff"
    colour4 = "BLACK"
    button_bg = "#05d7ff"
    button_fg = "#020f12"
    button_hover_bg = "#65e7ff"
    button_border_width = 1
    button_font = ("Arial", 10, "bold")

    def __init__(self, start_script, stop_script, open_images_folder):
        # Initialize variables
        self.screen_var = tk.StringVar()  # Initialize screen_var
        self.detection_threshold_var = tk.IntVar()  # Initialize detection_threshold_var
        self.click_randomness_var = tk.IntVar()  # Initialize click_randomness_var
        self.gray_scale_enabled = tk.BooleanVar()  # Initialize gray_scale_enabled
        self.move_duration_var = tk.IntVar()  # Initialize move_duration_var
        self.sleep_duration_var = tk.IntVar()  # Initialize sleep_duration_var

        # Create window
        self.root.title("TunasMaximax")
        self.root.geometry("800x550")  # Increased height
        self.root.resizable(width=False, height=False)

        # Set the background color of the window
        self.root.configure(bg=self.colour1)

        # Create frames
        self.left_frame = tk.Frame(self.root, bg=self.colour1, padx=10, pady=10)
        self.left_frame.grid(row=0, column=0, sticky=tk.NS, padx=(10, 0))
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=0)  # Row for Start button
        self.left_frame.rowconfigure(1, weight=0)  # Row for Stop button
        self.left_frame.rowconfigure(2, weight=0)  # Row for Add Images button
        self.left_frame.rowconfigure(3, weight=0)  # Row for Checkbox
        self.left_frame.rowconfigure(4, weight=0)  # Row for Checkbox
        self.left_frame.rowconfigure(5, weight=0)  # Row for Checkbox
        self.left_frame.rowconfigure(6, weight=0)  # Row for Checkbox

        self.right_frame = tk.Frame(self.root, bg=self.colour1, padx=10, pady=10)
        self.right_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)

        # Create buttons and checkbox
        self.initButtons(start_script, stop_script, open_images_folder)

        # Create status label
        self.initStatusLabel()

        # Create log area
        self.initLogArea()

        # Setup logging
        self.setup_logging()

        # Load configuration
        self.load_configuration()

        # Run exit script on window close
        self.root.protocol("WM_DELETE_WINDOW", self.exit_script)

    def createButton(self, text, command, parent_frame):
        button = tk.Button(
            parent_frame,
            text=text,
            command=command,
            bg=self.button_bg,
            fg=self.button_fg,
            font=self.button_font,
            relief="flat",
            borderwidth=self.button_border_width,
            width=20,
            height=2,
            highlightthickness=0,
        )
        button.bind("<Enter>", self.on_enter)
        button.bind("<Leave>", self.on_leave)
        return button

    def initButtons(self, start_script, stop_script, open_images_folder):
        # Start button
        self.start_button = self.createButton("Start", start_script, self.left_frame)
        self.start_button.grid(column=0, row=1, pady=5, sticky=tk.W)

        # Stop Button
        self.stop_button = self.createButton("Stop", stop_script, self.left_frame)
        self.stop_button.grid(column=0, row=2, pady=5, sticky=tk.W)

        # Open Select Folder Button
        self.select_button = self.createButton(
            "Select images", self.open_select_window, self.left_frame
        )
        self.select_button.grid(column=0, row=3, pady=5, sticky=tk.W)

        # Add Images Button
        self.add_images_button = self.createButton(
            "Open images", open_images_folder, self.left_frame
        )
        self.add_images_button.grid(column=0, row=4, pady=5, sticky=tk.W)

        # Open Config Button
        self.config_button = self.createButton(
            "Configuration", self.open_config_window, self.left_frame
        )
        self.config_button.grid(column=0, row=5, pady=5, sticky=tk.W)

        # Exit Button
        self.exit_button = self.createButton("Exit", self.exit_script, self.left_frame)
        self.exit_button.grid(column=0, row=6, pady=5, sticky=tk.W)  # Moved to row 9

    def initStatusLabel(self):
        self.status_label = tk.Label(
            self.left_frame,
            text="Status: Stopped",
            bg=self.colour1,
            fg=self.colour2,
            font=self.button_font,
        )
        self.status_label.grid(column=0, row=7, pady=10, sticky=tk.W)  # Moved to row 10

    def initLogArea(self):
        # Create a Text widget
        self.log_area = tk.Text(
            self.right_frame,
            wrap=tk.WORD,
            height=30,
            width=75,
            background=self.colour1,
            foreground=self.colour2,
            selectbackground=self.colour3,
            selectforeground=self.colour4,
            blockcursor=True,
            borderwidth=0,
        )
        self.log_area.grid(column=0, row=0, pady=10, sticky=tk.W)

        # Enable scrolling with mouse wheel
        self.log_area.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def setup_logging(self):
        # Create and configure a custom logging handler
        handler = TkinterLogHandler(self.log_area)
        # Set the level to capture all messages
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        # Add the custom handler to the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def on_mouse_wheel(self, event):
        self.log_area.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # Buttons hover animations
    def on_leave(self, event):
        event.widget.configure(bg=self.button_bg)

    def on_enter(self, event):
        event.widget.configure(bg=self.button_hover_bg)

    def getScreenVar(self):
        pattern = r"Screen (\d+)"
        match = re.search(pattern, self.screen_var.get())
        return int(match.group(1)) - 1

    def load_images_from_folders(self, folders):
        config_images_list = self.config["selected_images"]
        images = []
        for folder in folders:
            base_folder_path = os.path.join(images_folder, folder)
            if os.path.exists(base_folder_path):
                for filename in os.listdir(base_folder_path):
                    img_path = os.path.join(base_folder_path, filename)
                    if os.path.isfile(img_path) and filename.lower().endswith(
                        (".png", ".jpg", ".jpeg", ".bmp", ".gif")
                    ):
                        # Open the image and append the PIL Image object to the list
                        logging.info(f"Load {re.sub(r"^.*images\\", "", img_path)}")
                        images.append(Image.open(img_path))
            else:
                config_images_list.remove(folder)
        self.save_configuration({"selected_images": config_images_list}, False)
        return images

    def load_configuration(self):
        self.get_config()
        # Load screen selection and checkbox state
        if "grays_scale_state" in self.config:
            self.gray_scale_enabled.set(self.config["grays_scale_state"])
        if "detection_threshold" in self.config:
            self.detection_threshold_var.set(self.config["detection_threshold"])
        if "click_randomness" in self.config:
            self.click_randomness_var.set(self.config["click_randomness"])
        if "move_duration" in self.config:
            self.move_duration_var.set(self.config["move_duration"])
        if "sleep_duration" in self.config:
            self.sleep_duration_var.set(self.config["sleep_duration"])
        if "selected_images" in self.config:
            self.selected_images = self.config["selected_images"]
            logging.info("-----Start Images Loading-----")
            self.loaded_images = self.load_images_from_folders(
                self.config["selected_images"]
            )
            if len(self.loaded_images) == 0:
                logging.info("No images to be loaded !")
                pyautogui.alert(
                    "No images were found, don't forget to add them and select them in the app !"
                )
            logging.info("-----Stop Images Loading-----")
        if "selected_screen" in self.config:
            selected_screen = self.config["selected_screen"]
            if selected_screen:
                self.screen_var.set(selected_screen)
            else:
                monitors = get_monitors()
                screen_options = [
                    f"Screen {
                    i + 1} ({screen.width}x{screen.height})"
                    for i, screen in enumerate(monitors)
                ]
                config = {"selected_screen": screen_options[0]}
                self.save_configuration(config)
                self.screen_var.set(screen_options[0])

    def save_configuration(self, config, load=True):
        new_config = {**self.config, **config}
        with open(config_path, "w") as file:
            json.dump(new_config, file)
            self.config = new_config
        if load:
            self.load_configuration()

    def get_config(self):
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                config = json.load(file)
                self.config = config
                return config

    def open_config_window(self):
        ConfigWindow(self.root, self)  # Open the configuration window

    def open_select_window(self):
        FolderSelectorApp(self.root, self)  # Open the select folder window

    def exit_script(self):
        logging.info("Exiting program!")
        self.root.quit()
