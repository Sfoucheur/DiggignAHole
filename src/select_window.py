import tkinter as tk
from tkinter import ttk
import os
import functools
from customWidgets.checkbox_treeview import CheckboxTreeview
import logging

script_dir = os.getcwd()
relative_images_folder_path = "assets/images"
images_folder_relative = os.path.join(script_dir, relative_images_folder_path)
images_folder = os.path.abspath(images_folder_relative)


class FolderSelectorApp:
    def __init__(self, parent, ui_instance):
        self.parent = parent
        self.ui_instance = ui_instance
        self.window = tk.Toplevel(parent)
        self.window.grab_set()
        self.window.title("Select images")
        self.window.geometry("500x400")
        self.window.resizable(width=True, height=True)
        self.window.configure(bg=self.ui_instance.colour1)
        self.config = self.ui_instance.get_config()

        # Configure main grid
        self.window.columnconfigure(0, weight=1)  # Main column for treeview and frames
        self.window.rowconfigure(0, weight=0)  # Search frame row
        self.window.rowconfigure(1, weight=1)  # Treeview row, expand
        self.window.rowconfigure(2, weight=0)  # Buttons row

        # Search frame
        self.search_frame = tk.Frame(self.window, bg=self.ui_instance.colour1)
        self.search_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="ew")

        # Treeview frame
        self.treeview_frame = tk.Frame(self.window, bg=self.ui_instance.colour1)
        self.treeview_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")

        # Buttons frame
        self.buttons_frame = tk.Frame(self.window, bg=self.ui_instance.colour1)
        self.buttons_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Configure column weights for frames
        self.search_frame.columnconfigure(0, weight=1)  # Search bar expands
        self.search_frame.columnconfigure(1, weight=0)  # Reset button does not expand
        self.treeview_frame.columnconfigure(0, weight=1)  # Treeview should expand
        self.buttons_frame.columnconfigure(
            0, weight=1
        )  # Buttons in single row, expand evenly
        self.buttons_frame.columnconfigure(1, weight=1)
        self.buttons_frame.columnconfigure(2, weight=1)

        # Create and style buttons
        self.create_search()
        self.create_treeview()
        self.create_buttons()
        self.setup_styles()
        self.load_folders()
        self.window.protocol("WM_DELETE_WINDOW", self.exit_script)

    def on_checked(self, items, checked):
        if checked:
            self.config["selected_images"].append(
                *[
                    self.get_full_path(item_id).replace("\\ ", "\\").strip()
                    for item_id in items
                ]
            )
        else:
            self.config["selected_images"].remove(
                *[
                    self.get_full_path(item_id).replace("\\ ", "\\").strip()
                    for item_id in items
                ]
            )

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

    def create_treeview(self):
        # Create and pack the CheckboxTreeview widget
        self.tree_scrollbar = ttk.Scrollbar(self.treeview_frame)
        self.tree_scrollbar.grid(row=0, column=1, sticky="ns", pady=10)

        self.tree = CheckboxTreeview(
            self.treeview_frame, yscrollcommand=self.tree_scrollbar.set
        )
        self.tree.setOnCheck(self.on_checked)
        self.tree["show"] = "tree"

        # Make the Treeview expand within the frame
        self.tree.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # Set the frame's row and column weight to allow expansion
        self.treeview_frame.rowconfigure(0, weight=1)
        self.treeview_frame.columnconfigure(0, weight=1)

        self.tree_scrollbar.config(command=self.tree.yview)

    def create_search(self):
        self.search_var = tk.StringVar()
        self.search_bar = ttk.Entry(self.search_frame, textvariable=self.search_var)
        self.search_bar.grid(row=0, column=0, sticky="ew")

        self.reset_button = ttk.Button(
            self.search_frame,
            text="Reset",
            style="Custom.TButton",
            command=self.reset_search,
        )
        self.reset_button.grid(row=0, column=1, padx="5", sticky="e")
        self.search_bar.bind("<KeyRelease>", self.filter_items)

    def create_buttons(self):
        # Create buttons with custom styling
        self.collapse_button = ttk.Button(
            self.buttons_frame,
            text="Collapse All",
            style="Custom.TButton",
            command=self.collapse_all,
        )
        self.collapse_button.grid(row=0, column=0, padx="10", pady="10", sticky="ew")

        self.uncheck_button = ttk.Button(
            self.buttons_frame,
            text="Uncheck All",
            style="Custom.TButton",
            command=self.uncheck_all,
        )
        self.uncheck_button.grid(row=0, column=1, padx="10", pady="10", sticky="ew")

        self.select_button = ttk.Button(
            self.buttons_frame,
            text="Save",
            style="Custom.TButton",
            command=self.save_images_config,
        )
        self.select_button.grid(row=0, column=2, padx="10", pady="10", sticky="ew")

    def exit_script(self):
        self.window.destroy()
        self.window.grab_release()

    def get_directory_structure(self, root_dir: str):
        """Create a dictionary that represents the folder structure of directory."""
        folder_structure = {}
        root_dir = root_dir.rstrip(os.sep)
        start = root_dir.rfind(os.sep) + 1

        for path, dirs, _ in os.walk(root_dir):
            folders = path[start:].split(os.sep)
            subdir = {}
            parent = functools.reduce(
                lambda d, key: d.setdefault(key, {}), folders[:-1], folder_structure
            )
            parent[folders[-1]] = subdir
        return folder_structure["images"]

    def load_folders(self):
        # Get the folder structure as a nested dictionary
        self.folder_structure = {}
        self.folder_structure[""] = self.get_directory_structure(images_folder)
        # Populate the treeview with the folder structure
        self.populate_treeview(self.folder_structure)

    def populate_treeview(self, folder_structure):
        self.tree.delete(*self.tree.get_children())  # Clear existing items
        self._add_folders_to_treeview("", folder_structure[""])

    def _add_folder_recursive(self, insert_id, folder_structure):
        nodes_found = set()

        """Recursively add folders to the treeview based on the given folder_structure."""
        for folder, subfolders in folder_structure.items():
            folder_id = self.tree.insert(
                insert_id, "end", text=" " + folder, open=False
            )

            full_path = self.get_full_path(folder_id)

            if full_path in self.config["selected_images"]:
                nodes_found.add(folder_id)  # Add the folder_id to the set

            # Recursively find and add nodes from subfolders
            nodes_found.update(self._add_folder_recursive(folder_id, subfolders))

        return nodes_found

    def _add_folders_to_treeview(self, insert_id, folder_structure):
        # First, add folders to the tree view and collect nodes found
        nodes_found = self._add_folder_recursive(insert_id, folder_structure)

        # Then, process all nodes found
        self.process_checked_nodes(nodes_found)

    def process_checked_nodes(self, nodes):
        for folder_id in nodes:
            self.tree.change_state(folder_id, "checked")

        for folder_id in nodes:
            self.tree._check_ancestor(folder_id)

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
                filtered_subfolders = self._filter_folders(subfolders, search_term)
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

    def save_images_config(self):
        self.ui_instance.save_configuration(self.config)
        self.window.destroy()

    def get_full_path(self, item_id):
        path_parts = []
        current_id = item_id

        while current_id:
            item_text = self.tree.item(current_id, "text").strip()
            path_parts.append(item_text)
            current_id = self.tree.parent(current_id)

        path_parts.reverse()
        return os.path.join(*path_parts).replace("\\ ", "\\")
