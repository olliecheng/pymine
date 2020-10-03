from .datatypes import Target, Position
from .data import mobs, items, blocks
from .exceptions import CommandError

import requests
import aiohttp
import asyncio
import sys
import atexit

from typing import Union, Iterable


DEFAULT = ""

session = None


def cleanup_session():
    if session:
        asyncio.get_event_loop().run_until_complete(session.close())


atexit.register(cleanup_session)


async def async_execute_command(command: str, catch_errors: bool = True):
    global session

    # remove defaults
    command = command.rstrip()

    if not session:
        session = aiohttp.ClientSession()

    # print(command)
    try:
        # r = requests.get(f"http://127.0.0.1:8080/{command}")
        r = await session.get(f"http://127.0.0.1:8080/{command}")
    except aiohttp.client_exceptions.ClientConnectorError:
        # server not running!
        print(
            "Server not running. Make sure that the Pymine Server application is open!"
        )

        sys.exit(1)  # oh no...
        # oh lord jesus what are you doing
        # please stop it

    response = (await r.json())["body"]
    if response.get("error", "") == "minecraft-not-connected":
        print(
            "Minecraft not connected to the server. Make sure you've run `/connect localhost:19131` from inside the Minecraft Client."
        )

        sys.exit(2)  # he does it again. god damn it

    if catch_errors and response["statusCode"]:
        raise CommandError(
            message=response["statusMessage"], code=response["statusCode"]
        )

    return response


def execute_command(command: str, catch_errors: bool = True):
    return asyncio.get_event_loop().run_until_complete(
        async_execute_command(command, catch_errors)
    )


async def async_execute_commands_simultaneously(
    commands: Iterable[str], catch_errors: bool = True
):
    futures = []

    for command in commands:
        task = async_execute_command(command, catch_errors)
        futures.append(task)

    results = await asyncio.gather(*futures)
    return results


def execute_commands_simultaneously(commands: Iterable[str], catch_errors: bool = True):
    return asyncio.get_event_loop().run_until_complete(
        async_execute_commands_simultaneously(commands, catch_errors)
    )


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


def say(message: str):
    return execute_command(f"say {message}")


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
