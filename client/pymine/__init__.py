from .datavalues import ENTITIES
from .datatypes import Target
from .data import mobs


def example():
    v = Target(Target.Entities, type=[mobs.sheep])
    print(v)
