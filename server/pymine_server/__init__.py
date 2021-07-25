from .main import start_server, create_server_thread
from .tray import create_tray, run_tray


def run_program():
    icon = create_tray()
    t = create_server_thread(icon=icon)
    icon.run()
