from cx_Freeze import setup, Executable
import sys

build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = 'Brain Signal',
    version = '0.1',
    description = 'Brain Signal',
	options = {"build_exe": build_exe_options},
    executables = [Executable('main.py')]
)