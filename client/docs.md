# pymine-client documentation

# User commands


### clone
```py
clone(begin, end, destination, maskMode, cloneMode)

Examples:
clone(Pos(1, 1, 1), Pos(3, 3, 3), Pos(5, 5, 5))
clone(
    begin = Pos(1, 1, 1),
    end = Pos(3, 3, 3),
    destination = Pos(5, 5, 5),
    maskMode = "masked",
    cloneMode = "move"
)
```
**Clones one region of blocks into another area.**
<br><br>

begin: Position: one opposing corner of the region to copy.  
end: Position: the other opposing corner of the region to copy.  
destination: Position: the lower northwest corner of the destination region.
maskMode (optional):  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `"replace"` (default) to copy all blocks and overwrite blocks in the destination  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `"masked"` to copy only non-air blocks, and not overwrite blocks with air  
cloneMode (optional):  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `"force"`: force the clone even if there is overlap  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `"move"`: delete the original region after the copy, so it is effectively 'moved'  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; `"normal"` (default): don't move or force.  

<br>

---

### executeasother
```py
executeasother(origin, position, command)
```
**Execute another command as the specified target.**
<br><br>

origin: Target: the target to execute the command. Must be a player name or selector.  
position: Position: the position from which to run the command.  
command: String: the Minecraft command to run.  

<br>

---

### fill
```py
fill(from_, to, tileName, tileData, oldBlockHandling)

Examples:
fill(Pos(1, 1, 1), Pos(3, 3, 3), blocks.podzol)
fill(
    from_ = Pos(1, 1, 1),
    to = Pos(3, 3, 3),
    tileName = blocks.podzol,
)
```
**Fills a region with a specified block.**
<br><br>

from_: Position: one opposing corner of the region to fill.  
to: Position: the other opposing corner of the region to fill.  
tileName: Block: the block to fill the region with.  

Information on the optional tileData (int) and oldBlockHandling (str) parameters can be found on the [wiki](https://minecraft.fandom.com/wiki/Commands/fill)

<br>

---

### replace
```py
replace(from_, to, newTileName, tileNameToReplace, newTileData, replacedTileDataValue)

Examples:
replace(Pos(1, 1, 1), Pos(3, 3, 3), blocks.grass, blocks.podzol)
  Replaces all podzol with grass in the region from (1,1,1) to (3,3,3)
```
**Replaces all blocks within a region with another block.**
<br><br>

from_: Position: one opposing corner of the region to replace.  
to: Position: the other opposing corner of the region to replace.  
newTileName: Block: matching blocks in the region will be replaced with this block.  
tileNameToReplace: Block: the block to replace  

Information on the optional newTileData (int) and replacedTileDataValue (str) parameters can be found on the [wiki](https://minecraft.fandom.com/wiki/Commands/fill)

<br>

---

### give
```py
give(item_name, amount, target, data)

Examples:
give(items.baked_potato, 64)
  Gives 64 baked potatoes to the nearest player.
```
**Gives items to players.**
<br><br>

item_name: Item: item to give  
amount (Optional): integer: the number of items to give  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; defaults to 1  
target (Optional): Entity: the player selector or name to give items to  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; defaults to nearest player  
data (Optional): integer: item data (check wiki)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; defaults to 0  

<br>

---

### kill
```py
kill(target)

Examples:
kill(entities.chicken)
  Kills all chickens.
```
**Kill entities or players.**

target: Entity: entity to kill.

