from pymine import *

say("I call this popcorn chicken...")

for i in range(50):
    summon(entities.chicken.type[0], Pos("~5", "~1", "~0"))

say("Pop!")

kill(entities.chicken)
kill(entities.item)
