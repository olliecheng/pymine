from PIL import Image
import pyperclip
import pystray
from pystray import Menu as menu, MenuItem as item

from .utils.logging import getLogger

log = getLogger("tray")


def load_icon(filePath: str = "icon.png") -> Image:
    from pathlib import Path

    # default icon "icon.png" from https://www.deviantart.com/alice-sakura18/art/Minecraft-Pixel-Icon-Free-To-Use-656207545
    img_path = Path(__file__) / "../resources" / filePath
    log.debug(f"Icon path: {img_path.resolve()}")
    im = Image.open(img_path.resolve())
    im.load()  # releases the file lock

    return im


def copy_to_clipboard(icon: pystray.Icon, port: int) -> None:
    text_to_copy = f"/connect localhost:{port}"
    pyperclip.copy(text_to_copy)

    icon.notify("Copied to clipboard!")
    log.debug("Copy to clipboard: " + text_to_copy)


def quit_handler(icon: pystray.Icon) -> None:
    icon.stop()


def create_menu(port: int) -> menu:
    NO_ACTION = lambda _: None
    return menu(
        item("pymine server", NO_ACTION, enabled=False),
        item(f"Active on port {port}", NO_ACTION, enabled=False),
        item("", NO_ACTION, enabled=False),
        item("Type the following command into Minecraft:", NO_ACTION, enabled=False),
        item(
            f"/connect localhost:{port}",
            lambda icon: copy_to_clipboard(icon=icon, port=port),
            enabled=True,
            default=True,
        ),
        item("(click above to copy)", NO_ACTION, enabled=False,),
        item("", NO_ACTION, enabled=False),
        item("WS: 19132, HTTP: 19133", NO_ACTION, enabled=False),
        item("Quit", quit_handler, enabled=True),
    )


def create_tray(port: int = 19131) -> pystray.Icon:
    icon = pystray.Icon("pymine", load_icon(), menu=create_menu(port=port))
    return icon


def run_tray() -> None:
    icon = create_tray()
    log.info("Created tray icon")
    icon.run(setup=lambda icon: icon.notify("Pymine server initiated!"))
