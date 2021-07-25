from .server import start_server, create_server_thread
from .tray import create_tray, run_tray


def run_program(port: int = 19131):
    icon = create_tray(port=port)
    t = create_server_thread(icon=icon, port=port)
    icon.run()
