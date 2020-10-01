from .datatypes import Target, Position
from .data import mobs, items, blocks
from .exceptions import CommandError

import requests
import sys

from typing import Union


DEFAULT = ""


def execute_command(command):
    # remove defaults
    command = command.rstrip()

    # print(command)
    try:
        r = requests.get(f"http://127.0.0.1:8080/{command}")
    except requests.exceptions.ConnectionError:
        # server not running!
        print(
            "Server not running. Make sure that the Pymine Server application is open!"
        )

        sys.exit(1)  # oh no...
        # oh lord jesus what are you doing
        # please stop it

    response = r.json()["body"]
    if response.get("error", "") == "minecraft-not-connected":
        print(
            "Minecraft not connected to the server. Make sure you've run `/connect localhost:19131` from inside the Minecraft Client."
        )

        sys.exit(2)  # he does it again. god damn it

    if response["statusCode"]:
        raise CommandError(
            message=response["statusMessage"], code=response["statusCode"]
        )

    return response


def clone(
    begin: Position,
    end: Position,
    destination: Position,
    maskMode: str = DEFAULT,
    cloneMode: str = DEFAULT,
    tileName: str = DEFAULT,
):
    return execute_command(f"clone {begin} {end} {destination} {maskMode} {cloneMode}")


def executeasother(target: Target, position: Position, command: str):
    return execute_command(f"executeasother {target} {position} {command}")


def fill(
    from_: Position,
    to: Position,
    tileName: str,
    tileData: int = DEFAULT,
    oldBlockHandling: str = DEFAULT,
    replaceTileName: str = DEFAULT,
    replaceDataValue: str = DEFAULT,
):
    return execute_command(
        f"fill {from_} {to} {tileName} {tileData} {oldBlockHandling} {replaceTileName} {replaceDataValue}"
    )


def give(
    item_name: str,
    *,
    target: Target = Target.NearestPlayer,
    amount: int = 1,
    data: int = 0,
):
    return execute_command(f"give {target} {item_name} {amount} {data}")


def kill(target: str):
    return execute_command(f"kill {target}")


def setblock(
    position: Position,
    tileName: str,
    tileData: int = DEFAULT,
    oldBlockHandling: str = DEFAULT,
):
    return execute_command(
        f"setblock {position} {tileName} {tileData} {oldBlockHandling}"
    )


def summon(entityType: str, spawnPos: Position):
    return execute_command(f"summon {entityType} {spawnPos}")


def testforblock(position: Position, tileName: str, dataValue: int = DEFAULT):
    return execute_command(f"testforblock {position} {tileName} {dataValue}")


def testforblocks(
    begin: Position, end: Position, destination: Position, mode: str = DEFAULT
):
    return execute_command(f"testforblocks {begin} {end} {destination} {mode}")


def timeset(time: Union[str, int]):
    return execute_command(f"time set {time}")


def teleport(
    target: Target,
    destination: Union[Position, Target],
    xrot: int = DEFAULT,
    yrot: int = DEFAULT,
):
    return execute_command(f"teleport {target} {destination} {yrot} {xrot}")


def weather(type: str, duration: int = DEFAULT):
    return execute_command(f"weather {type} {duration}")
