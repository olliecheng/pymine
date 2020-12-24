import csv
from os import path
from collections import namedtuple


def parse_entity_IDs():
    entities = {}

    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "data", "entityIDs.csv"))

    with open(filepath, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for line, row in enumerate(csv_reader):
            if line == 0:
                continue

            entities[row["name"].lower()] = row["namespaced_id"].lower()

    import pprint
    import clipboard

    clipboard.copy(pprint.pformat(entities))

    return entities


def parse_item_IDs():
    items = set()

    basepath = path.dirname(__file__)
    filepath = path.abspath(path.join(basepath, "data", "itemIDs.txt"))

    with open(filepath, mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter="\t")

        for line, row in enumerate(csv_reader):
            if line % 2:
                # odd
                items.add(row[0].split(":")[1][:-2])

    items = sorted(list(items))
    print(items)
    print(len(items))

    with open("data/items.py", "w") as f:
        for item in items:
            f.write(f'{item} = "{item}"\n')


if __name__ == "__main__":
    ENTITIES = parse_entity_IDs()
    parse_item_IDs()
