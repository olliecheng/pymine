from .datatypes import Target, Position, BaseTarget
from .data import entities, items, blocks

from .exceptions import CommandError

import requests
import aiohttp
import aiohttp.client_exceptions
import asyncio
import sys
import atexit

from typing import Union, Iterable, Optional, Any


DEFAULT = ""
OptionalInt = Union[str, int]
OptionalStr = str


session = None


def cleanup_session():
    if session:
        asyncio.get_event_loop().run_until_complete(session.close())


atexit.register(cleanup_session)


async def async_execute_command(command: str, catch_errors: bool = False):
    global session

    # remove defaults
    command = command.rstrip()

    if not session:
        session = aiohttp.ClientSession()

    # print(command)
    try:
        # r = requests.get(f"http://127.0.0.1:19133/{command}")
        r = await session.get(f"http://127.0.0.1:19133/{command}")
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


def execute_command(command: str, catch_errors: bool = False):
    return asyncio.get_event_loop().run_until_complete(
        async_execute_command(command, catch_errors)
    )


async def async_execute_commands_simultaneously(
    commands: Iterable[str], catch_errors: bool = False
):
    futures = []

    for command in commands:
        task = async_execute_command(command, catch_errors)
        futures.append(task)

    results = await asyncio.gather(*futures)
    return results


def execute_commands_simultaneously(
    commands: Iterable[str], catch_errors: bool = False
):
    return asyncio.get_event_loop().run_until_complete(
        async_execute_commands_simultaneously(commands, catch_errors)
    )


def clone(
    begin: Position,
    end: Position,
    destination: Position,
    maskMode: OptionalStr = DEFAULT,
    cloneMode: OptionalStr = DEFAULT,
    tileName: OptionalStr = DEFAULT,
):
    return execute_command(f"clone {begin} {end} {destination} {maskMode} {cloneMode}")


def executeasother(target: Target, position: Position, command: str):
    return execute_command(f"executeasother {target} {position} {command}")


def fill(
    from_: Position,
    to: Position,
    tileName: str,
    tileData: int = 0,
    oldBlockHandling: OptionalStr = DEFAULT,
):
    return execute_command(
        f"fill {from_} {to} {tileName} {tileData} {oldBlockHandling}",
        catch_errors=False,
    )


def replace(
    from_: Position,
    to: Position,
    newTileName: str,
    tileNameToReplace: OptionalStr = DEFAULT,
    newTileData: int = 0,
    replacedTileDataValue: OptionalStr = DEFAULT,
):
    return execute_command(
        f"fill {from_} {to} {newTileName} {newTileData} replace {tileNameToReplace} {replacedTileDataValue}",
        catch_errors=False,
    )


def give(
    item_name: str,
    *,
    target: Target = entities.player_nearest,
    amount: int = 1,
    data: int = 0,
):
    return execute_command(f"give {target} {item_name} {amount} {data}")


def kill(target: Union[str, BaseTarget]):
    return execute_command(f"kill {target}", catch_errors=False)


def removeblock(position: Position):
    setblock(position, blocks.air)


def say(message: str):
    return execute_command(f"say {message}")


def setblock(
    position: Position,
    tileName: str,
    tileData: OptionalInt = DEFAULT,
    oldBlockHandling: OptionalStr = DEFAULT,
):
    return execute_command(
        f"setblock {position} {tileName} {tileData} {oldBlockHandling}",
        catch_errors=False,
    )


def summon(entityType: Target, spawnPos: Position):
    if isinstance(entityType, BaseTarget):
        if entityType.selector != "@e":
            raise CommandError(message="Can only summon entities!", code=0)
        elif isinstance(entityType.type, list):
            if len(entityType.type) > 1:
                raise CommandError(
                    message="Target entity can only have 1 type.", code=0
                )
            entityType = entityType.type[0]
        else:
            entityType = str(entityType.type)

    return execute_command(f"summon {entityType} {spawnPos}")


def testforblock(position: Position, tileName: str, dataValue: OptionalInt = DEFAULT):
    # print(
    #     execute_command(
    #         f"testforblock {position} {tileName} {dataValue}", catch_errors=False
    #     )
    # )
    return execute_command(
        f"testforblock {position} {tileName} {dataValue}", catch_errors=False
    )["matches"]


def testforblocks(
    begin: Position, end: Position, destination: Position, mode: OptionalStr = DEFAULT
):
    return execute_command(f"testforblocks {begin} {end} {destination} {mode}")


def timeset(time: Union[str, int]):
    return execute_command(f"time set {time}")


def teleport(
    target: Target,
    destination: Union[Position, Target],
    xrot: OptionalInt = DEFAULT,
    yrot: OptionalInt = DEFAULT,
):
    return execute_command(f"teleport {target} {destination} {yrot} {xrot}")


def weather(type: str, duration: OptionalInt = DEFAULT):
    return execute_command(f"weather {type} {duration}")
