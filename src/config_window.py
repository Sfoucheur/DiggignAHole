# config_window.py

import tkinter as tk
from tkinter import ttk
from screeninfo import get_monitors


class ConfigWindow:
    def __init__(self, parent, ui_instance):
        self.parent = parent
        self.ui_instance = ui_instance
        self.window = tk.Toplevel(parent)
        self.window.grab_set()
        self.window.title("Configuration")
        self.window.geometry("400x300")
        self.window.resizable(width=False, height=False)
        self.window.configure(bg=self.ui_instance.colour1)

        # Intialize config vars
        self.screen_var = tk.StringVar()  # Initialize screen_var
        self.detection_threshold_var = tk.IntVar()  # Initialize detection_threshold_var
        self.click_randomness_var = tk.IntVar()  # Initialize click_randomness_var
        self.gray_scale_enabled = tk.BooleanVar()  # Initialize gray_scale_enabled
        self.move_duration_var = tk.IntVar()  # Initialize move_duration_var
        self.sleep_duration_var = tk.IntVar()  # Initialize sleep_duration_var

        self.screen_var.set(self.ui_instance.screen_var.get())
        self.detection_threshold_var.set(self.ui_instance.detection_threshold_var.get())
        self.click_randomness_var.set(self.ui_instance.click_randomness_var.get())
        self.gray_scale_enabled.set(self.ui_instance.gray_scale_enabled.get())
        self.move_duration_var.set(self.ui_instance.move_duration_var.get())
        self.sleep_duration_var.set(self.ui_instance.sleep_duration_var.get())

        # Create and configure frames
        self.create_frames()

        # Initialize configuration elements
        self.initScreenSelect()
        self.initDetectionThresholdInput()
        self.initClickRandomnessInput()
        self.initMoveDurationInput()
        self.initSleepDurationInput()
        self.initCheckbox()

        # Create a Save button to save configuration changes
        save_button = tk.Button(
            self.window,
            text="Save",
            command=self.save_configuration,
            bg=self.ui_instance.button_bg,
            fg=self.ui_instance.button_fg,
            font=self.ui_instance.button_font,
            relief="flat",
            borderwidth=self.ui_instance.button_border_width,
            width=50,
            height=2,
        )
        save_button.grid(row=6, column=0, columnspan=2, pady=10, sticky=tk.EW)
        self.window.protocol("WM_DELETE_WINDOW", self.exit_script)

    def exit_script(self):
        self.window.destroy()
        self.window.grab_release()

    def create_frames(self):
        """Create frames for organizing configuration elements."""
        self.main_frame = tk.Frame(self.window, bg=self.ui_instance.colour1)
        # Make sure the grid expands properly
        for i in range(8):
            self.main_frame.rowconfigure(i, weight=1)
        for i in range(2):
            self.main_frame.columnconfigure(i, weight=1)
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

    def initScreenSelect(self):
        self.screen_label = tk.Label(
            self.main_frame,
            text="Selected Screen",
            bg=self.ui_instance.colour1,
            fg=self.ui_instance.colour2,
            font=self.ui_instance.button_font,
        )
        self.screen_label.grid(row=0, column=0, pady=5, sticky=tk.W)

        self.screen_menu = ttk.Combobox(
            self.main_frame, textvariable=self.screen_var, state="readonly"
        )
        self.screen_menu.grid(row=0, column=1, pady=5, sticky=tk.W)

        self.update_screen_options()

    def initDetectionThresholdInput(self):
        self.detection_threshold_label = tk.Label(
            self.main_frame,
            text="Detection Threshold",
            bg=self.ui_instance.colour1,
            fg=self.ui_instance.colour2,
            font=self.ui_instance.button_font,
        )
        self.detection_threshold_label.grid(row=1, column=0, pady=5, sticky=tk.W)

        self.detection_threshold_entry = tk.Spinbox(
            self.main_frame,
            from_=0,
            to=100,
            increment=1,
            textvariable=self.detection_threshold_var,
            state="readonly",
        )
        self.detection_threshold_entry.grid(row=1, column=1, pady=5, sticky=tk.W)

    def initClickRandomnessInput(self):
        self.click_randomness_label = tk.Label(
            self.main_frame,
            text="Click Randomness",
            bg=self.ui_instance.colour1,
            fg=self.ui_instance.colour2,
            font=self.ui_instance.button_font,
        )
        self.click_randomness_label.grid(row=2, column=0, pady=5, sticky=tk.W)

        self.click_randomness_entry = tk.Spinbox(
            self.main_frame,
            from_=0,
            to=50,
            increment=1,
            textvariable=self.click_randomness_var,
            state="readonly",
        )
        self.click_randomness_entry.grid(row=2, column=1, pady=5, sticky=tk.W)

    def initMoveDurationInput(self):
        self.move_duration_label = tk.Label(
            self.main_frame,
            text="Move duration",
            bg=self.ui_instance.colour1,
            fg=self.ui_instance.colour2,
            font=self.ui_instance.button_font,
        )
        self.move_duration_label.grid(row=3, column=0, pady=5, sticky=tk.W)

        self.move_duration_entry = tk.Spinbox(
            self.main_frame,
            from_=0,
            to=100,
            increment=5,
            textvariable=self.move_duration_var,
            state="readonly",
        )
        self.move_duration_entry.grid(row=3, column=1, pady=5, sticky=tk.W)

    def initSleepDurationInput(self):
        self.sleep_duration_label = tk.Label(
            self.main_frame,
            text="Sleep duration",
            bg=self.ui_instance.colour1,
            fg=self.ui_instance.colour2,
            font=self.ui_instance.button_font,
        )
        self.sleep_duration_label.grid(row=4, column=0, pady=5, sticky=tk.W)

        self.sleep_duration_entry = tk.Spinbox(
            self.main_frame,
            from_=100,
            to=5000,
            increment=100,
            textvariable=self.sleep_duration_var,
            state="readonly",
        )
        self.sleep_duration_entry.grid(row=4, column=1, pady=5, sticky=tk.W)

    def initCheckbox(self):
        self.checkbox = tk.Checkbutton(
            self.main_frame,
            text="Enable GrayScale",
            variable=self.gray_scale_enabled,
            bg=self.ui_instance.colour1,
            fg=self.ui_instance.colour2,
            font=self.ui_instance.button_font,
            relief="flat",
        )
        self.checkbox.grid(row=5, column=0, columnspan=2, pady=5, sticky=tk.W)

    def update_screen_options(self):
        screens = get_monitors()
        screen_options = [
            f"Screen {
            i + 1} ({screen.width}x{screen.height})"
            for i, screen in enumerate(screens)
        ]
        self.screen_menu["values"] = screen_options

        # Set default value to the first screen
        if screens:
            self.ui_instance.screen_var.set(screen_options[0])

    def save_configuration(self):
        config = {
            "selected_screen": self.screen_var.get(),
            "grays_scale_state": self.gray_scale_enabled.get(),
            "detection_threshold": self.detection_threshold_var.get(),
            "click_randomness": self.click_randomness_var.get(),
            "move_duration": self.move_duration_var.get(),
            "sleep_duration": self.sleep_duration_var.get(),
        }
        self.ui_instance.save_configuration(config)
        self.window.destroy()
