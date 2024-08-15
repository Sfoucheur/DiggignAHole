from pathlib import Path
import tkinter as tk
from tkinter import ttk
import os
import functools
from customWidgets.checkbox_treeview import CheckboxTreeview

script_dir = Path(__file__).resolve().parent
relative_images_folder_path = "../images"
images_folder = (script_dir / relative_images_folder_path).resolve()


class FolderSelectorApp:
    def __init__(self, parent, ui_instance):
        self.parent = parent
        self.ui_instance = ui_instance
        self.window = tk.Toplevel(parent)
        self.window.grab_set()
        self.window.title("Select images")
        self.window.geometry("600x400")
        self.window.resizable(width=True, height=True)
        self.window.configure(bg=self.ui_instance.colour1)

        # Frame for search bar and reset button
        self.search_frame = tk.Frame(self.window, bg=self.ui_instance.colour1)
        self.search_frame.grid(
            row=0, column=0, sticky="ew", padx=20, pady=(20, 0))

        # Create and pack the search bar and reset button
        self.search_var = tk.StringVar()
        self.search_bar = ttk.Entry(
            self.search_frame, textvariable=self.search_var)
        self.search_bar.grid(row=0, column=0, sticky="ew")
        self.search_bar.bind("<KeyRelease>", self.filter_items)

        self.reset_button = ttk.Button(
            self.search_frame,
            text="Reset",
            style="Custom.TButton",
            command=self.reset_search,
        )
        self.reset_button.grid(row=0, column=1, padx="5", columnspan=9)

        # Create and pack the CheckboxTreeview widget
        self.tree = CheckboxTreeview(self.window)
        self.tree["show"] = "tree"
        self.tree.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)

        # Create and style buttons
        self.create_buttons()

        # Configure grid weights
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Configure the row for buttons
        self.window.grid_rowconfigure(2, weight=0)

        self.setup_styles()
        self.load_folders()
        self.window.protocol("WM_DELETE_WINDOW", self.exit_script)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")

        # Style for Treeview (affects CheckboxTreeview indirectly)
        style.configure(
            "Treeview",
            background=self.ui_instance.colour1,
            foreground=self.ui_instance.colour2,
            fieldbackground=self.ui_instance.colour1,
            borderwidth=0,
        )

        style.map(
            "Treeview",
            background=[("selected", self.ui_instance.colour1)],
            foreground=[("selected", self.ui_instance.colour2)],
        )

        # Style for Buttons
        style.configure(
            "Custom.TButton",
            background=self.ui_instance.button_bg,
            foreground=self.ui_instance.button_fg,
            font=self.ui_instance.button_font,
            borderwidth=self.ui_instance.button_border_width,
            relief="flat",
        )
        style.map(
            "Custom.TButton",
            background=[("active", self.ui_instance.button_hover_bg)],
            foreground=[("active", self.ui_instance.button_fg)],
        )

    def create_buttons(self):
        # Create buttons with custom styling
        self.collapse_button = ttk.Button(
            self.window,
            text="Collapse All",
            style="Custom.TButton",
            command=self.collapse_all,
        )
        self.collapse_button.grid(
            row=2, column=0, sticky="w", padx="10", pady="10")

        self.uncheck_button = ttk.Button(
            self.window,
            text="Uncheck All",
            style="Custom.TButton",
            command=self.uncheck_all,
        )
        self.uncheck_button.grid(row=2, column=0, padx="10", pady="10")

        self.select_button = ttk.Button(
            self.window,
            text="Print Selected Items",
            style="Custom.TButton",
            command=self.print_selected_items,
        )
        self.select_button.grid(
            row=2, column=0, sticky="e", padx="10", pady="10")

    def exit_script(self):
        self.window.destroy()
        self.window.grab_release()

    def get_directory_structure(self, root_dir):
        """Create a dictionary that represents the folder structure of directory."""
        folder_structure = {}
        root_dir = root_dir.rstrip(os.sep)
        start = root_dir.rfind(os.sep) + 1

        for path, dirs, _ in os.walk(root_dir):
            folders = path[start:].split(os.sep)
            subdir = {}
            parent = functools.reduce(
                lambda d, key: d.setdefault(
                    key, {}), folders[:-1], folder_structure
            )
            parent[folders[-1]] = subdir

        return folder_structure[root_dir]

    def load_folders(self):
        # Get the folder structure as a nested dictionary
        self.folder_structure = {}
        self.folder_structure[""] = self.get_directory_structure(
            images_folder.as_posix()
        )
        # Populate the treeview with the folder structure
        self.populate_treeview(self.folder_structure)

    def populate_treeview(self, folder_structure):
        self.tree.delete(*self.tree.get_children())  # Clear existing items
        self._add_folders_to_treeview("", folder_structure[""])

    def _add_folders_to_treeview(self, insert_id, folder_structure):
        """Recursively add folders to the treeview based on the given folder_structure."""
        for folder, subfolders in folder_structure.items():
            folder_id = self.tree.insert(
                insert_id, "end", text=" " + folder, open=False
            )
            self._add_folders_to_treeview(folder_id, subfolders)

    def filter_items(self, event):
        search_term = self.search_var.get().lower()
        if search_term:
            self._apply_filter("", search_term)
        else:
            self.reset_filter()

    def _apply_filter(self, parent_id, search_term):
        self.tree.delete(*self.tree.get_children())  # Clear all items
        filtered_structure = self._filter_folders(
            self.folder_structure[parent_id], search_term
        )
        self._add_folders_to_treeview(parent_id, filtered_structure)
        self.tree.expand_all()

    def _filter_folders(self, folder_structure, search_term):
        """Recursively filter folders based on the search term."""
        filtered_structure = {}
        for folder, subfolders in folder_structure.items():
            if search_term in folder.lower():
                filtered_structure[folder] = subfolders
            else:
                filtered_subfolders = self._filter_folders(
                    subfolders, search_term)
                if filtered_subfolders:
                    filtered_structure[folder] = filtered_subfolders
        return filtered_structure

    def reset_filter(self):
        # Reset and reload the original folder structure
        self.populate_treeview(self.folder_structure)

    def reset_search(self):
        self.search_var.set("")
        self.reset_filter()

    def collapse_all(self):
        self.tree.collapse_all()

    def uncheck_all(self):
        self.tree.uncheck_all()

    def print_selected_items(self):
        checked_ids = self.tree.get_checked()
        for item_id in checked_ids:
            full_path = self.get_full_path(item_id)
            print(f"Item Full Path: {full_path}")

    def get_full_path(self, item_id):
        path_parts = []
        current_id = item_id

        while current_id:
            item_text = self.tree.item(current_id, "text")
            path_parts.append(item_text)
            current_id = self.tree.parent(current_id)

        path_parts.reverse()
        return os.path.join(*path_parts)
