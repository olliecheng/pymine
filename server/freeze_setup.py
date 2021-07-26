import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["pymine_server", "pystray._win32", "websockets.legacy.server"],
    "include_msvcr": True,
    "silent": True,
}

msi_data = {
    "ProgId": [
        (
            "denosawr.pymine_server",
            None,
            None,
            "Server exposing a programmatic interface to Minecraft: Education Edition",
            "mainIcon",
            None,
        ),
    ],
    "Icon": [("mainIcon", "pymine_server/resources/icon.ico"),],
}

bdist_msi_options = {
    "add_to_path": True,
    "data": msi_data,
    "upgrade_code": "{e5c7572f-d727-4fa8-ab68-8ae95827f3ed}",
    "summary_data": {
        "author": "Ollie Cheng",
        "comments": "Server exposing a programmatic interface to Minecraft: Education Edition",
    },
    "install_icon": "pymine_server/resources/icon.ico",
}

setup(
    name="pymine-server",
    version="0.1",
    description="Server exposing a programmatic interface to Minecraft: Education Edition",
    options={"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
    executables=[
        Executable(
            "run.py",
            target_name="pymine-server",
            base="Win32GUI",
            shortcut_name="Pymine Server",
            shortcut_dir="ProgramMenuFolder",
            copyright="https://github.com/denosawr/pymine",
            icon="pymine_server/resources/icon.ico",
        ),
        Executable(
            "run.py",
            target_name="pymine-server-console",
            copyright="https://github.com/denosawr/pymine",
            icon="pymine_server/resources/icon.ico",
        ),
    ],
)
