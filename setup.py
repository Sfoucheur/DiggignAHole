from cx_Freeze import setup, Executable
import sys
import os

# Define the path to the folder you want to include
assets = "assets/"

build_exe_options = {
    "build_exe": "build/kamsoutrax",
    "include_files": [assets],
    "optimize": 2,
}

sys.path.append(os.path.realpath(sys.path[0] + "\\src"))

setup(
    name="Kamas",
    version="1.0",
    description="Collect everything",
    options={"build_exe": build_exe_options},
    executables=[Executable("src/main.py")],
)
