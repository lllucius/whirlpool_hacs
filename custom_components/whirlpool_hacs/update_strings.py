#!/usr/bin/python

import json
from collections import OrderedDict

def entity_type(model: dict[str, str]):
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
    return None

def merge_dicts(dict1, dict2):
    """
    Merge two multilevel dictionaries, overwriting values for overlapping keys.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if isinstance(value, dict):
            result[key] = merge_dicts(result.get(key, {}), value)
        else:
            result[key] = value
    return result

def asdf():    
    def fixname(cc: str):
        out = ""
        for c in cc:
            if c.isupper() and out:
                out = out + " "
            out = out + c
        return out

    def remove_prefix(items: list[str]):
        values = list(items.values())
        prefix = values[0]
        for value in values[1:]:
            while not value.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return items
        new = {}
        for k, v in items.items():
            new[v] = v[len(prefix):]
        return new

    with open("old.json", "r") as f:
        old = json.loads(f.read())

    with open("/home/yam/whirlpool-sixth-sense/models/ddww") as f:
        attrs = json.loads(f.read())

    with open("/tmp/strings.json", "w") as f:
        entities = {}
        #for app in appliances_manager.get_appliances():
        del attrs["dataModel"]["id"]
        for app in attrs["dataModel"]:
            #for attr in app.data_attrs:
            for attr in attrs["dataModel"][app]:
                platform = entity_type(attr)
                if attr["Instance"] and platform:
                    name = fixname(attr["AttributeName"])
                    mapped = attr["MappedAttributeName"]
                    if platform not in entities:
                        entities[platform] = {}
                    entities[platform][mapped] = {
                       "name": name
                    }
                    if "EnumValues" in attr:
                        state = {}
                        for k, v in remove_prefix(attr["EnumValues"]).items():
                            state[k] = fixname(v)
                        entities[platform][mapped]["state"] = state

        strings = {"entities": entities}

        new = merge_dicts(old, strings)
        f.write(json.dumps(new, sort_keys=True))

asdf()
