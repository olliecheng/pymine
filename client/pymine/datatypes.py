from __future__ import annotations
from typing import Optional, Union, List

from . import datavalues


class Relative:
    def __init__(self, val: int):
        self.val = val

    def __str__(self) -> str:
        return f"^{self.val}"


Coordinate = Union[int, Relative, str]


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

        self.coords = constructor or " ".join(coordinates_ls)

    def __str__(self) -> str:
        return self.coords


Position = Union[Pos, str]


class Target:
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
        type: Optional[Union[List[str], str]] = None,
    ):
        # hacky asf
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

        self.arguments = [
            f"{trait_lookup[k]}={v}" for k, v in params.items() if v != None
        ]

        self.arguments = []
        for k, v in params.items():
            if v == None:
                continue

            trait_name = trait_lookup[k]
            if __builtins__["type"](v) == list:
                for j in v:
                    self.arguments.append(f"{trait_name}={j}")
            else:
                self.arguments.append(f"{trait_name}={v}")

        self.selector = selector

    def __str__(self) -> str:
        return f"{self.selector}[{','.join(self.arguments)}]"
