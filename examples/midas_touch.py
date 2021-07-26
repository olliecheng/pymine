from pymine import *

say("Anything I touch turns to gold..!")
while True:
    block_position = Pos("~", "~-1", "~")
    if not testforblock(block_position, blocks.air):
        setblock(block_position, blocks.gold_block)
