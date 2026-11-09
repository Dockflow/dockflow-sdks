# Dockflow API v3 SDKs

Official client libraries for the [Dockflow API](https://docs.dockflow.com/api), generated from its OpenAPI spec.

| Language | Package |
|---|---|
| TypeScript / JavaScript | `npm install @dockflow/sdk` |
| Python | `pip install dockflow-sdk` |
| C# / .NET | `dotnet add package Dockflow.Sdk` |
| Java | `com.dockflow:dockflow-sdk` (Maven Central) |
| PHP | `composer require dockflow/dockflow-sdk` |

Authenticate with a Dockflow API key; the SDKs send it as `Authorization: Bearer <key>`. The UAT sandbox is `https://uat.dockflow.com`, production is `https://api.dockflow.com`.

## How this repo works

- `spec/v3.json` is the published Dockflow v3 contract (`https://api.dockflow.com/v3/openapi.json`).
- `scripts/generate.sh` generates every SDK into `build/` with openapi-generator.
- `scripts/normalise.py` narrows two "one item or a list" unions to their list form (the API accepts it, every generator can compile it) and gives operations their public names: `UpstreamApi.getUpstream`, `TradeflowsApi.createTradeflows` / `deleteTradeflow`, `DocumentsApi.*`, `WidgetApi.searchWidget`.

## Releases

After every production deploy, Dockflow/infrastructure sends a `spec-updated` dispatch (plus a daily run as a safety net), and `sync.yml` fetches the published spec. When it changed, it builds all five SDKs against it, picks the next version (`oasdiff`: a breaking change bumps the minor while on 0.x, anything else the patch), commits `spec/v3.json` and `VERSION`, tags `vX.Y.Z` and runs `publish.yml`:

| Registry | Auth |
|---|---|
| PyPI | Trusted publishing (environment `pypi`) |
| NuGet | Trusted publishing (environment `nuget`, owner org Dockflow) |
| npm | Trusted publishing; `NPM_TOKEN` only for the first release |
| Maven Central | `MAVEN_CENTRAL_*` token and `MAVEN_GPG_*` signing key |
| Packagist | `PHP_DEPLOY_KEY` pushes `build/php` to Dockflow/dockflow-php, which Packagist tracks |

## Licence

MIT
