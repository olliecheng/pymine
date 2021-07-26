from pymine import *
import random


def random_flower_position():
    while True:
        coords = (random.randint(-10, 10), random.randint(-10, 10))
        # check if coordinate is a grass block
        if testforblock(Pos(coords[0], 3, coords[1]), blocks.grass) and testforblock(
            Pos(coords[0], 4, coords[1]), blocks.air
        ):
            break
    return Pos(coords[0], 4, coords[1])


def main_game():
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

if __name__ == "__main__":
    main_game()
