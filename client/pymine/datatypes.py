from __future__ import annotations
from typing import Optional, Union

import builtins

Numeric = Union[int, float]


class Relative:
    def __init__(self, val: Numeric):
        self.val = val

    def __str__(self) -> str:
        return f"~{self.val}"


Coordinate = Union[Numeric, Relative, str]


class Pos:
    def __init__(
        self,
        x: Optional[Coordinate] = None,
        y: Optional[Coordinate] = None,
        z: Optional[Coordinate] = None,
        constructor: Optional[str] = None,
    ):
        # create a coordinates string
        coordinates_ls = [str(i) for i in (x, y, z) if i != None]

        if constructor and len(coordinates_ls):
            raise TypeError("Cannot give both constructor and x, y, z coordinates!")
        elif len(coordinates_ls) != 3:
            raise TypeError("Must give x, y, and z coordinates.")

        self.x = x
        self.y = y
        self.z = z

        self.coords = constructor or " ".join(coordinates_ls)

    def __str__(self) -> str:
        return self.coords

    def translate(self, x_trans: int = 0, y_trans: int = 0, z_trans: int = 0) -> Pos:
        try:
            for v in (self.x, self.y, self.z):
                assert isinstance(v, int)
                if isinstance(v, str):
                    raise Exception("Translation only works with exact values.")
        except Exception:
            return

        return Pos(self.x + x_trans, self.y + y_trans, self.z + z_trans)


Position = Union[Pos, str]


class BaseTarget:
    NearestPlayer = "@p"
    RandomPlayer = "@r"
    AllPlayers = "@a"
    Entities = "@e"
    Agent = "@c"

    def __init__(
        self,
        selector: str,
        gamemode: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        z: Optional[int] = None,
        distance_min: Optional[int] = None,
        distance_max: Optional[int] = None,
        experience_level_min: Optional[int] = None,
        experience_level_max: Optional[int] = None,
        type: Optional[Union[list[str], str]] = None,
    ):
        self.type = type

        # just to make pyright shut up about unused variable access...
        gamemode, x, y, z, distance_min, distance_max, experience_level_min, experience_level_max, type

        # retrieves all parameters and collects them in a dict
        # similar to **params, but features type hinting
        params = {k: v for k, v in locals().items() if not k in {"selector", "self"}}

        trait_lookup = {
            "gamemode": "m",
            "x": "x",
            "y": "y",
            "z": "z",
            "distance_min": "rm",
            "distance_max": "r",
            "experience_level_min": "lm",
            "experience_level_max": "l",
            "type": "type",
        }

        self.arguments = []
        for k, v in params.items():
            if v == None:
                continue

            trait_name = trait_lookup[k]

            # notice how `type` is an argument for this class' constructor.
            # in order to use the `type()` function, we have to reference builtins.
            # this is because the intended target for this library is
            # learners and beginners, who I feel would be confused by an
            # alternative name parameter avoiding namespace collisions,
            # such as type_.
            if builtins.type(v) == list:
                for j in v:
                    self.arguments.append(f"{trait_name}={j}")
            else:
                self.arguments.append(f"{trait_name}={v}")

        self.selector = selector

    def __str__(self) -> str:
        return f"{self.selector}[{','.join(self.arguments)}]"


Target = Union[BaseTarget, str]
