from cx_Freeze import setup, Executable

# Define the path to the folder you want to include
assets_folder = './images'
config = './config.json'


build_exe_options = {
    'include_files': [assets_folder, config],
}

setup(
    name="Kamas",
    version="1.0",
    description="Collect everything",
    options={'build_exe': build_exe_options},
    executables=[Executable("main.py")]
)
