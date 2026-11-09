# Dockflow API v3 SDKs

Official client libraries for the [Dockflow API](https://docs.dockflow.com/api), generated from its OpenAPI spec.

| Language | Package |
|---|---|
| TypeScript / JavaScript | `npm install @dockflow/sdk` |
| Python | `pip install dockflow-sdk` |
| C# / .NET | `dotnet add package Dockflow.Sdk` |
| Java | `com.dockflow:dockflow-sdk` (Maven Central) |
| PHP | `composer require dockflow/dockflow-sdk` |

Authenticate with an API key (`Authorization: <key>`). The UAT sandbox is `https://uat.dockflow.com`, production is `https://api.dockflow.com`.

## How this repo works

- `spec/v3.json` is the published Dockflow v3 contract (`https://api.dockflow.com/v3/openapi.json`).
- `scripts/generate.sh` generates every SDK into `build/` with openapi-generator.
- `scripts/normalise.py` narrows two "one item or a list" unions to their list form, which the API accepts and which every generator can compile.

## Licence

MIT
