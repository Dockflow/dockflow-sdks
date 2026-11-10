"""Write the registry README for one generated SDK, replacing the generator's.
Usage: python3 readme.py <language> <out.md> <version>
"""
import sys

lang, out, version = sys.argv[1], sys.argv[2], sys.argv[3]

SDKS = {
    "typescript": ("TypeScript / JavaScript", "@dockflow/sdk", "npm install @dockflow/sdk", "typescript", """\
import { Configuration, UpstreamApi } from "@dockflow/sdk";

const upstream = new UpstreamApi(
  new Configuration({ basePath: "https://api.dockflow.com", accessToken: process.env.DOCKFLOW_KEY }),
);
const page = await upstream.getUpstream({ tradeflow: "PO4564268" });"""),
    "python": ("Python", "dockflow-sdk", "pip install dockflow-sdk", "python", """\
import os
from dockflow_sdk import ApiClient, Configuration, UpstreamApi

config = Configuration(host="https://api.dockflow.com", access_token=os.environ["DOCKFLOW_KEY"])
with ApiClient(config) as client:
    page = UpstreamApi(client).get_upstream(tradeflow="PO4564268")"""),
    "csharp": ("C# / .NET", "Dockflow.Sdk", "dotnet add package Dockflow.Sdk", "csharp", """\
using Dockflow.Sdk.Api;
using Dockflow.Sdk.Client;

var upstream = new UpstreamApi(new Configuration
{
    BasePath = "https://api.dockflow.com",
    AccessToken = Environment.GetEnvironmentVariable("DOCKFLOW_KEY"),
});
var page = upstream.GetUpstream(tradeflow: "PO4564268");"""),
    "java": ("Java", "com.dockflow:dockflow-sdk", None, "java", """\
import com.dockflow.sdk.ApiClient;
import com.dockflow.sdk.api.UpstreamApi;

ApiClient client = new ApiClient();
client.updateBaseUri("https://api.dockflow.com");
client.setRequestInterceptor(r -> r.header("Authorization", "Bearer " + System.getenv("DOCKFLOW_KEY")));
var page = new UpstreamApi(client).getUpstream(null, "PO4564268", null, null, null, null, null, null, null, null, null);"""),
    "php": ("PHP", "dockflow/dockflow-sdk", "composer require dockflow/dockflow-sdk", "php", """\
$config = Dockflow\\Sdk\\Configuration::getDefaultConfiguration()
    ->setHost('https://api.dockflow.com')
    ->setAccessToken(getenv('DOCKFLOW_KEY'));
$upstream = new Dockflow\\Sdk\\Api\\UpstreamApi(new GuzzleHttp\\Client(), $config);
$page = $upstream->getUpstream(tradeflow: 'PO4564268');"""),
}

name, package, install, fence, example = SDKS[lang]
if install is None:
    install_block = f"""Maven:

```xml
<dependency>
  <groupId>com.dockflow</groupId>
  <artifactId>dockflow-sdk</artifactId>
  <version>{version}</version>
</dependency>
```

Gradle: `implementation("com.dockflow:dockflow-sdk:{version}")`"""
else:
    install_block = f"```sh\n{install}\n```"

open(out, "w").write(f"""# Dockflow API SDK for {name}

The official {name} client for the [Dockflow](https://dockflow.com) API v3: container and shipment tracking events,
tradeflows, documents and the tracking widget.

## Install

{install_block}

## Quickstart

Create an API key in the Dockflow console. Production is `https://api.dockflow.com`; test against the UAT sandbox at
`https://uat.dockflow.com` with a UAT key.

```{fence}
{example}
```

The four API classes are `UpstreamApi`, `TradeflowsApi`, `DocumentsApi` and `WidgetApi`.

## Documentation

- Guides and examples: https://docs.dockflow.com/api/sdk/
- OpenAPI 3.1 spec: https://api.dockflow.com/v3/openapi.json
- All five SDKs (TypeScript, Python, C#, Java, PHP): https://github.com/Dockflow/dockflow-sdks

## Versioning

Released automatically whenever the API changes. Versions follow semver: a breaking API change bumps the major
version, everything else the minor or patch.

## License

MIT
""")
