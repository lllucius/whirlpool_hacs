#!/usr/bin/python

import json
import os

def entity_type(model: dict[str, str]):
    """ Determime the platform for a given attribute. """
    if model["DataType"] == "Boolean":
        if model["DeviceIO"] == "RO":
            return "binary_sensor"
        if model["DeviceIO"] == "RW":
            return "switch"
        if model["DeviceIO"] == "WO":
            return "button"
    elif model["DataType"] == "enum":
        if model["DeviceIO"] == "RO":
            return "sensor"
        if model["DeviceIO"] == "RW":
            return "select"
    elif "Integer" in model["DataType"]:
        if model["DeviceIO"] == "RO":
            return "sensor"
        if model["DeviceIO"] == "RW":
            return "number"

    return None

def remove_prefix(items: dict[str, str]):
    """ Determine if all values in the dict have a shared prefix.

        In this example the prefix would be "Prefix":
            {
                "1", "PrefixOne",
                "2", "PrefixTwo",
                "3", "PrefixThree"
            }
    """
    values = list(items.values())
    prefix = values[0]
    for value in values[1:]:
        while not value.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                prefix = ""
                break

    """ Handle cases like this where the "unique" part of the name all start with
        the same character. Only allows for a single upper case character:
        {
            "1", "PrefixOn",
            "2", "PrefixOff"
        }
    """
    if prefix and prefix[-1].isupper():
        prefix = prefix[:-1]

    """ Rebuild the dict using the original value as the key and value with the
        prefix removed.
    """
    new = {}
    for k, v in items.items():
        new[v] = v[len(prefix):] if len(values) > 1 else v
    return new

def fixname(cc: str):
    """ Break camelcased string into individual words. """
    out = ""
    for c in cc:
        if c.isupper() and out:
            out = out + " "
        out = out + c
    return out

def merge(target, source):
    """ merge the two """

    # Merge models into strings taking care not to replace any of
    # the existing strings.
    added = 0
    for model in models:
        attrs = model["dataModel"]["attributes"]
        for attr in attrs:
            platform = entity_type(attr)
            if attr["Instance"] and platform:
                if platform not in entity:
                    entity[platform] = {}

                name = fixname(attr["AttributeName"])
                m2m = attr["M2MAttributeName"]
                if m2m not in entity[platform]:
                    added = added + 1
                    entity[platform][m2m] = {
                        "name": name
                    }
                if "EnumValues" in attr:
                    if "state" not in entity[platform][m2m]:
                        entity[platform][m2m]["state"] = {}

                    state = {}
                    for k, v in remove_prefix(attr["EnumValues"]).items():
                        if k not in entity[platform][m2m]["state"]:
                            added = added + 1
                            entity[platform][m2m]["state"][k] = fixname(v)


def update_strings():
    """ Merge all models into existing strings. """

    # Load all files in the data_models directory
    models = []
    for file in os.scandir("data_models"):
        if file.is_file():
            with open(file.path, "r") as f:
                s = json.load(f)
                models.append(s)

    for file in ["strings.json"] + [file.path for file in os.scandir("translations")]:
        # Load the existing strings
        strings = {"entity": {}}
        with open(file, "r") as f:
            strings = json.load(f)
        entity = strings["entity"]

        # Merge models into strings taking care not to replace any of
        # the existing strings.
        added = 0
        for model in models:
            attrs = model["dataModel"]["attributes"]
            for attr in attrs:
                platform = entity_type(attr)
                if attr["Instance"] and platform:
                    if platform not in entity:
                        entity[platform] = {}

                    name = fixname(attr["AttributeName"])
                    m2m = attr["M2MAttributeName"]
                    if m2m not in entity[platform]:
                        added = added + 1
                        entity[platform][m2m] = {
                            "name": name
                        }

                    if "EnumValues" in attr:
                        if "state" not in entity[platform][m2m]:
                            entity[platform][m2m]["state"] = {}

                        state = {}
                        for k, v in remove_prefix(attr["EnumValues"]).items():
                            if k not in entity[platform][m2m]["state"]:
                                added = added + 1
                                entity[platform][m2m]["state"][k] = fixname(v)

        if added:
            strings["entity"] = entity
            with open(f"{file}.new", "w") as f:
                json.dump(strings, f, indent=2, sort_keys=True)

            print(f"Added {added} entries to {file}.new.")

update_strings()

