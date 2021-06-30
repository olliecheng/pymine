from pymine import *

import asyncio
import random
from typing import Sequence

from pprint import pprint

import sys


async def lever_on(resp):
    results = await async_execute_commands_simultaneously(
        [f"testforblock 104 64 -3 lever {i}" for i in range(8, 17)], catch_errors=False
    )
    return any([x["matches"] == True for x in results])


def random_flower_position():
    while True:
        coords = (random.randint(-10, 10), random.randint(-10, 10))
        # check if coordinate is a grass block
        if testforblock(Pos(coords[0], 3, coords[1]), blocks.grass) and testforblock(
            Pos(coords[0], 4, coords[1]), blocks.air
        ):
            break
    return Pos(coords[0], 4, coords[1])


def example():
    timeout = 15

    random_flower_position()

    replace(Pos(-10, 4, -10), Pos(10, 4, 10), blocks.air, blocks.red_flower)
    replace(
        Pos(-10, 4, -10),
        Pos(10, 5, 10),
        blocks.air,
        blocks.double_plant,
    )
    replace(Pos(-10, 3, -10), Pos(10, 3, 10), blocks.grass, blocks.podzol)

    execute_command("title @p times 0 400 0")  # 20 ticks = 1s

    timeset("day")
    setblock(Pos(11, 4, 0), blocks.air)
    kill(entities.zombie)

    wait_for_player_movement(check_x=11, check_z=0)
    print("Went through doorway >_>")

    setblock(Pos(11, 4, 0), blocks.cobblestone_wall)
    timeset("midnight")
    summon(entities.lightning_bolt, Pos(0, 4, 0))
    say("Welcome to the graveyard of lost souls...")

    flowers = []

    while True:
        for flower in flowers:
            flower[1] += 1

            position = flower[0]
            stage = flower[1]

            # https://minecraft.gamepedia.com/Flower#Block_data
            if stage == 0:
                setblock(position, blocks.red_flower, 3)  # Azure Bluet
            elif stage == 1:
                setblock(position, blocks.red_flower, 0)  # Poppy
            elif stage == 2:
                setblock(position, blocks.double_plant, 4)  # Rose Bush
            else:
                removeblock(position)
                setblock(position.translate(y_trans=-1), blocks.grass)
                summon(entities.zombie, position)

        flowers = [x for x in flowers if x[1] != 3]

        new_flower = random_flower_position()
        flowers.append([new_flower, 0])
        setblock(new_flower, blocks.red_flower, 3)  # Azure Bluet
        setblock(new_flower.translate(y_trans=-1), blocks.podzol)

        execute_command('titleraw @a title {"rawtext": [{"text": " "}]}')
        execute_command(f"title @a subtitle {len(flowers)} left")

        start_time = time.time()
        while True:
            try:
                timeout_duration = timeout - (time.time() - start_time)

                if timeout_duration < 0.3:
                    break

                r = wait_for_block_broken(
                    (blocks.red_flower, blocks.double_plant), timeout=timeout_duration
                )
                # pprint.pprint(r)

                if r["block_name"] in ("red_flower", "double_plant"):
                    # test all flowers...
                    commands = []
                    for flower in flowers:
                        commands.append(
                            "testforblock {} {} {}".format(
                                flower[0],
                                *{
                                    0: ("red_flower", 3),
                                    1: ("red_flower", 0),
                                    2: ("double_plant", 4),
                                }[flower[1]],
                            )
                        )
                    results = [
                        x["matches"] for x in execute_commands_simultaneously(commands)
                    ]
                    for idx, result in enumerate(results):
                        if not result:
                            setblock(
                                flowers[idx][0].translate(y_trans=-1), blocks.grass
                            )
                            del flowers[idx]

                    kill(entities.item)

                execute_command('titleraw @a title {"rawtext": [{"text": " "}]}')
                execute_command(f"title @a subtitle {len(flowers)} left")

            except EventTimeout:
                pass

        timeout = max(timeout - 1, 5)


def ex3():
    while True:

        def filter_func(resp):
            testforblock(
                Pos(104, 64, -3),
                blocks.lever,
            )

        r = wait_for_event("ItemInteracted", timeout=0)
        pprint.pprint(r)
    # pprint.pprint(wait_for_event("ItemCrafted", lambda x: True, timeout=0))


def test():
    import time

    start = time.time()
    results = execute_commands_simultaneously(
        [f"testforblock 104 64 -3 lever {i}" for i in range(8, 17)], catch_errors=False
    )
    print(any([x["matches"] == True for x in results]))
    print(time.time() - start)
    # import pprint

    # pprint.pprint(results)


def examplea():
    # asyncio.get_event_loop().run_until_complete(test())
    # test()

    print("Start")
    import time

    # clone(Pos(98, 62, 2), Pos(100, 63, -2), Pos(100, 70, -2))

    say("I call this chicken popcorn...")

    s = time.time()
    for _ in range(100):
        summon(entities.chicken.type[0], Pos("~5", "~1", "~0"))

    say("Pop!")

    kill(entities.chicken)
    kill(entities.item)
    print(time.time() - s)
