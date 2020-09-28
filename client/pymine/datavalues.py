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


ENTITIES = parse_entity_IDs()
