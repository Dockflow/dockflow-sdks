"""Prepare the v3 spec for the generators: list-form unions and public SDK names.

Narrows the two 'X or list of X' unions to their canonical list form.

The API accepts both forms; the SDK always sends the list form. C#/Java generators
cannot compile anyOf-with-array unions, so the SDK's copy of the spec drops the
shorthand branches. Fails loudly if the spec no longer has the expected shapes.
Usage: python3 normalise.py <in.json> <out.json>
"""
import json
import re
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

# Public SDK names: these become class and method names, so renaming them later breaks every caller.
TAGS = {"TridentDocument": "Documents", "TridentDownstream": "Tradeflows",
        "TridentUpstream": "Upstream", "WidgetSearch": "Widget"}
OPERATIONS = {
    "documents-types": "listDocumentTypes", "trident-document-post": "uploadDocument",
    "trident-document-get": "getDocument", "trident-document-patch": "updateDocument",
    "trident-document-delete": "deleteDocument", "tridentDownstream.post": "createTradeflows",
    "tridentDownstream.delete": "deleteTradeflow", "tridentUpstream.get": "getUpstream",
    "widget-search": "searchWidget",
}


def public_name(name, capitalise):
    words = [w for w in re.split(r"[^A-Za-z0-9]+|(?<=[a-z])(?=[A-Z])", name) if w and w.lower() != "trident"]
    joined = "".join(w[:1].upper() + w[1:] for w in words)
    return joined if capitalise else joined[:1].lower() + joined[1:]


for item in spec["paths"].values():
    for method, op in item.items():
        if not isinstance(op, dict) or "operationId" not in op:
            continue
        op["operationId"] = OPERATIONS.get(op["operationId"]) or public_name(op["operationId"], False)
        op["tags"] = [TAGS.get(t) or public_name(t, True) for t in op.get("tags", [])]
spec["tags"] = [{**t, "name": TAGS.get(t["name"]) or public_name(t["name"], True)} for t in spec.get("tags", [])]

schemes = spec["components"].get("securitySchemes", {})
if "TridentToken" in schemes:
    schemes["ApiKey"] = {**schemes.pop("TridentToken"), "description": "A Dockflow API key, sent as `Authorization: Bearer <key>`."}
    spec["security"] = [{"ApiKey" if k == "TridentToken" else k: v for k, v in s.items()} for s in spec.get("security", [])]
    for item in spec["paths"].values():
        for op in item.values():
            if isinstance(op, dict) and "security" in op:
                op["security"] = [{"ApiKey" if k == "TridentToken" else k: v for k, v in s.items()} for s in op["security"]]

json.dump(spec, open(dst, "w"), indent=1)
print("normalise: narrowed 2 unions to list form, applied public names")
