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

# Public SDK names, keyed on method + path: those are the public contract, while docky's tags and
# operationIds follow internal class names that get renamed. These names become SDK classes and
# methods, so changing them later breaks every caller.
OPERATIONS = {
    ("get", "/v3/downstream/documents/types"): ("Documents", "listDocumentTypes"),
    ("post", "/v3/downstream/documents"): ("Documents", "uploadDocument"),
    ("get", "/v3/downstream/documents/{reference}"): ("Documents", "getDocument"),
    ("patch", "/v3/downstream/documents/{reference}"): ("Documents", "updateDocument"),
    ("delete", "/v3/downstream/documents/{reference}"): ("Documents", "deleteDocument"),
    ("post", "/v3/downstream/tradeflows"): ("Tradeflows", "createTradeflows"),
    ("delete", "/v3/downstream/tradeflows/{tradeflow_reference}"): ("Tradeflows", "deleteTradeflow"),
    ("get", "/v3/upstream"): ("Upstream", "getUpstream"),
    ("get", "/v3/widget/search"): ("Widget", "searchWidget"),
}


def derived(method, path):
    """Name for an operation added after this table was written, so a new endpoint never blocks a release."""
    words = [w for w in re.split(r"[^A-Za-z0-9]+", re.sub(r"\{[^}]*\}", "", path)) if w and w != "v3"]
    tag = words[0].capitalize() if words else "Default"
    op = method + "".join(w.capitalize() for w in words)
    return tag, op


used = set()
for path, item in spec["paths"].items():
    for method, op in item.items():
        if not isinstance(op, dict) or method not in ("get", "post", "put", "patch", "delete"):
            continue
        tag, name = OPERATIONS.get((method, path)) or derived(method, path)
        if name in used:
            sys.exit(f"normalise: duplicate operation name {name} for {method.upper()} {path}")
        used.add(name)
        op["operationId"], op["tags"] = name, [tag]
spec["tags"] = [{"name": t} for t in sorted({op["tags"][0] for item in spec["paths"].values()
                                              for op in item.values() if isinstance(op, dict) and "tags" in op})]

spec["info"]["description"] = "Client for the Dockflow API v3: upstream events, tradeflows, documents and the widget."

schemes = spec["components"].get("securitySchemes", {})
if "TridentToken" in schemes:
    schemes["ApiKey"] = schemes.pop("TridentToken")
    spec["security"] = [{"ApiKey" if k == "TridentToken" else k: v for k, v in s.items()} for s in spec.get("security", [])]

json.dump(spec, open(dst, "w"), indent=1)
print("normalise: narrowed 2 unions to list form, applied public names")
