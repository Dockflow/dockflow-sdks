"""Narrow the two 'X or list of X' unions in the v3 spec to their canonical list form.

The API accepts both forms; the SDK always sends the list form. C#/Java generators
cannot compile anyOf-with-array unions, so the SDK's copy of the spec drops the
shorthand branches. Fails loudly if the spec no longer has the expected shapes.
Usage: python3 sdk-normalise.py <in.json> <out.json>
"""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
spec = json.load(open(src))


def array_branch(union, where):
    branches = union.get("anyOf") or union.get("oneOf")
    arrays = [b for b in branches or [] if b.get("type") == "array"]
    if len(arrays) != 1:
        sys.exit(f"normalise: expected one array branch in {where}, found {len(arrays)}")
    return arrays[0]


body = spec["paths"]["/v3/downstream/tradeflows"]["post"]["requestBody"]["content"]["application/json"]
body["schema"] = array_branch(body["schema"], "POST /v3/downstream/tradeflows body")

props = spec["components"]["schemas"]["DownstreamTradeflow"]["properties"]
cref = props["container_reference"]
arr = array_branch(cref, "DownstreamTradeflow.container_reference")
objs = [b for b in arr["items"].get("anyOf", []) if b.get("type") == "object"]
if len(objs) != 1 or "reference" not in objs[0].get("properties", {}):
    sys.exit("normalise: container_reference items no longer have one {reference} object branch")
props["container_reference"] = {
    "description": cref.get("description", ""),
    "type": "array",
    "items": {**objs[0], "title": "ContainerReference"},
}

json.dump(spec, open(dst, "w"), indent=1)
print("normalise: narrowed 2 unions to list form")
