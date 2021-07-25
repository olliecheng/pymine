import sys
from cx_Freeze import setup, Executable

build_exe_options = {}

base = "Win32GUI"

setup(
    name="poetry-server",
    version="0.1",
    description="Server exposing a programmatic interface to Minecraft: Education Edition",
    options={"build_exe": build_exe_options},
    executables=[Executable("__main__.py", base=base)],
)
