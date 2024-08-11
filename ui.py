import tkinter as tk
from tkinter import ttk
import logging
import json
import os
import re
from screeninfo import get_monitors


class TkinterLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        try:
            msg = self.format(record)
            self.text_widget.configure(state=tk.NORMAL)
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.yview(tk.END)  # Scroll to the end
            self.text_widget.configure(state=tk.DISABLED)
        except Exception:
            self.handleError(record)


class Ui:
    root = tk.Tk()
    colour1 = '#020f12'  # Window background color
    colour2 = '#05d7ff'
    colour3 = '#65e7ff'
    colour4 = 'BLACK'
    button_bg = '#05d7ff'
    button_fg = '#020f12'
    button_hover_bg = '#65e7ff'
    button_border_width = 1
    button_font = ('Arial', 10, 'bold')

    CONFIG_FILE = 'config.json'

    def __init__(self, start_script, stop_script, exit_script, add_images_script):
        # Create window
        self.root.title("TunasMaximax")
        self.root.geometry('800x550')  # Increased height
        self.root.resizable(width=False, height=False)

        # Set the background color of the window
        self.root.configure(bg=self.colour1)

        # Create frames
        self.left_frame = tk.Frame(
            self.root, bg=self.colour1, padx=10, pady=10)
        self.left_frame.grid(row=0, column=0, sticky=tk.NS, padx=(10, 0))
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=0)  # Row for Start button
        self.left_frame.rowconfigure(1, weight=0)  # Row for Stop button
        self.left_frame.rowconfigure(2, weight=0)  # Row for Add Images button
        self.left_frame.rowconfigure(3, weight=0)  # Row for Checkbox
        # Row for Screen selection dropdown
        self.left_frame.rowconfigure(4, weight=0)
        # Row for Detection Threshold
        self.left_frame.rowconfigure(5, weight=0)
        self.left_frame.rowconfigure(6, weight=0)  # Row for Click Randomness
        self.left_frame.rowconfigure(7, weight=0)  # Row for spacing
        self.left_frame.rowconfigure(8, weight=0)  # Row for Exit button
        self.left_frame.rowconfigure(9, weight=0)  # Row for Status label
        self.left_frame.rowconfigure(10, weight=0)  # Row for Status label

        self.right_frame = tk.Frame(
            self.root, bg=self.colour1, padx=10, pady=10)
        self.right_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)

        # Create buttons and checkbox
        self.initButtons(start_script, stop_script,
                         exit_script, add_images_script)
        self.initCheckbox()
        self.initScreenSelect()
        self.initDetectionThresholdInput()
        self.initClickRandomnessInput()

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

    def initScreenSelect(self):
        self.screen_var = tk.StringVar()  # Store the screen description

        # Create a label for the combobox title
        self.screen_label = tk.Label(
            self.left_frame,
            text="Select Screen:",
            bg=self.colour1,
            fg=self.colour2,
            font=self.button_font
        )
        self.screen_label.grid(column=0, row=4, pady=5, sticky=tk.W)

        # Create the combobox
        self.screen_menu = ttk.Combobox(
            self.left_frame,
            textvariable=self.screen_var,
            state='readonly'
        )
        self.screen_menu.grid(column=0, row=5, pady=5, sticky=tk.W)

        # Populate screen options
        self.update_screen_options()

    def initDetectionThresholdInput(self):
        self.detection_threshold_var = tk.IntVar()
        self.detection_threshold_label = tk.Label(
            self.left_frame,
            text="Detection Threshold:",
            bg=self.colour1,
            fg=self.colour2,
            font=self.button_font
        )
        self.detection_threshold_label.grid(
            column=0, row=6, pady=5, sticky=tk.W)

        self.detection_threshold_entry = tk.Entry(
            self.left_frame,
            textvariable=self.detection_threshold_var,
            validate="key",
            validatecommand=(self.root.register(
                self.validate_detection_threshold), '%P')
        )
        self.detection_threshold_entry.grid(
            column=0, row=7, pady=5, sticky=tk.W)

    def initClickRandomnessInput(self):
        self.click_randomness_var = tk.IntVar()
        self.click_randomness_label = tk.Label(
            self.left_frame,
            text="Click Randomness:",
            bg=self.colour1,
            fg=self.colour2,
            font=self.button_font
        )
        self.click_randomness_label.grid(
            column=0, row=8, pady=5, sticky=tk.W)  # Moved to row 7

        self.click_randomness_entry = tk.Entry(
            self.left_frame,
            textvariable=self.click_randomness_var,
            validate="key",
            validatecommand=(self.root.register(
                self.validate_click_randomness), '%P')
        )
        self.click_randomness_entry.grid(
            column=0, row=9, pady=5, sticky=tk.W)  # Moved to row 8

    def createButton(self, text, command):
        button = tk.Button(
            self.left_frame,
            text=text,
            command=command,
            bg=self.button_bg,
            fg=self.button_fg,
            font=self.button_font,
            relief='flat',
            borderwidth=self.button_border_width,
            width=20,
            height=2,
            highlightthickness=0
        )
        button.bind("<Enter>", self.on_enter)
        button.bind("<Leave>", self.on_leave)
        return button

    def initButtons(self, start_script, stop_script, exit_script, add_images_script):
        # Start button
        self.start_button = self.createButton("Start", start_script)
        self.start_button.grid(column=0, row=0, pady=5, sticky=tk.W)

        # Stop Button
        self.stop_button = self.createButton("Stop", stop_script)
        self.stop_button.grid(column=0, row=1, pady=5, sticky=tk.W)

        # Add Images Button
        self.add_images_button = self.createButton(
            "Add images", add_images_script)
        self.add_images_button.grid(column=0, row=2, pady=5, sticky=tk.W)

        # Exit Button
        self.exit_button = self.createButton("Exit", self.exit_script)
        self.exit_button.grid(column=0, row=10, pady=5,
                              sticky=tk.W)  # Moved to row 9

    def initCheckbox(self):
        self.gray_scale_enabled = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(
            self.left_frame,
            text="Enable GrayScale",
            variable=self.gray_scale_enabled,
            bg=self.colour1,
            fg=self.colour2,
            font=self.button_font,
            relief='flat'
        )
        self.checkbox.grid(column=0, row=3, pady=5, sticky=tk.W)

    def initStatusLabel(self):
        self.status_label = tk.Label(
            self.left_frame, text="Status: Stopped", bg=self.colour1, fg=self.colour2)
        self.status_label.grid(column=0, row=11, pady=10,
                               sticky=tk.W)  # Moved to row 10

    def initLogArea(self):
        # Create a Text widget
        self.log_area = tk.Text(
            self.right_frame, wrap=tk.WORD, height=30, width=75, background=self.colour1, foreground=self.colour2, selectbackground=self.colour3, selectforeground=self.colour4, blockcursor=True, borderwidth=0
        )
        self.log_area.grid(column=0, row=0, pady=10, sticky=tk.W)

        # Enable scrolling with mouse wheel
        self.log_area.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def setup_logging(self):
        # Create and configure a custom logging handler
        handler = TkinterLogHandler(self.log_area)
        # Set the level to capture all messages
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the custom handler to the root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def on_mouse_wheel(self, event):
        self.log_area.yview_scroll(int(-1*(event.delta/120)), "units")

    # Buttons hover animations
    def on_leave(self, event):
        event.widget.configure(bg=self.button_bg)

    def on_enter(self, event):
        event.widget.configure(bg=self.button_hover_bg)

    def update_screen_options(self):
        screens = get_monitors()
        screen_options = [f"Screen {
            i + 1} ({screen.width}x{screen.height})" for i, screen in enumerate(screens)]
        self.screen_menu['values'] = screen_options

        # Set default value to the first screen
        if screens:
            self.screen_var.set(screen_options[0])

    def getScreenVar(self):
        pattern = r"Screen (\d+)"
        match = re.search(pattern, self.screen_var.get())
        return int(match.group(1)) - 1

    def load_configuration(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as file:
                config = json.load(file)
                # Load screen selection and checkbox state
                if 'selected_screen' in config:
                    selected_screen = config['selected_screen']
                    if selected_screen:
                        self.screen_var.set(selected_screen)
                if 'grays_scale_state' in config:
                    self.gray_scale_enabled.set(config['grays_scale_state'])
                if 'detection_threshold' in config:
                    self.detection_threshold_var.set(
                        config['detection_threshold'])
                if 'click_randomness' in config:
                    self.click_randomness_var.set(config['click_randomness'])

    def save_configuration(self):
        selected_screen = self.screen_var.get()
        config = {
            'selected_screen': selected_screen,
            'grays_scale_state': self.gray_scale_enabled.get(),
            'detection_threshold': self.detection_threshold_var.get(),
            'click_randomness': self.click_randomness_var.get()
        }
        with open(self.CONFIG_FILE, 'w') as file:
            json.dump(config, file)

    def validate_detection_threshold(self, value):
        try:
            value = int(value)
            if 0 <= value <= 100:
                self.detection_threshold_var.set(value)
                return True
        except ValueError:
            pass
        return False

    def validate_click_randomness(self, value):
        try:
            value = int(value)
            if value >= 0:
                self.click_randomness_var.set(value)
                return True
        except ValueError:
            pass
        return False

    def exit_script(self):
        self.save_configuration()
        logging.info('Exiting program!')
        self.root.quit()
