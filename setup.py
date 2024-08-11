from cx_Freeze import setup, Executable
import os

# Define the path to the folder you want to include
assets_folder = './images'
config = './config.json'


build_exe_options = {
    'include_files': [assets_folder, config]  # Include the assets folder
}

setup(
    name="TunasMaximax",
    version="0.1",
    description="Collect everything",
    options={'build_exe': build_exe_options},
    executables=[Executable("main.py")]
)
