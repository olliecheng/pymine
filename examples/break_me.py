from pymine import *

block_position = Pos(116, 72, -5)
say("Don't break this block!")
while True:
    wait_for_block_broken(block_position)
    say("Nu-uh!")
    setblock(block_position, blocks.diamond_block)
