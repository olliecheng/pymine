# from .datavalues import ENTITIES
import sys
from .datatypes import Target, Pos, Relative
from .data import entities, items, blocks
from .exceptions import CommandError

from .commands import *
from .events import *

from .ast_transform import (
    main,
    TransformError,
)

import inspect as _inspect
import re as _re


# print(_filename)
try:
    main()
except TransformError:
    pass
