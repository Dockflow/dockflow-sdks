#!/usr/bin/env bash
# Generate the SDKs from spec/v3.json into build/<language>.
# Usage: scripts/generate.sh [typescript python csharp java php]
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
GENERATOR_VERSION=7.27.0
VERSION=$(tr -d '[:space:]' < "$ROOT/VERSION")
OUT="$ROOT/build"
JAR="$ROOT/.cache/openapi-generator-cli-$GENERATOR_VERSION.jar"
REPO=https://github.com/Dockflow/dockflow-sdks

mkdir -p "$ROOT/.cache"
[ -s "$JAR" ] || curl -fsSL -o "$JAR" \
  "https://repo1.maven.org/maven2/org/openapitools/openapi-generator-cli/$GENERATOR_VERSION/openapi-generator-cli-$GENERATOR_VERSION.jar"

mkdir -p "$OUT"
python3 "$ROOT/scripts/normalise.py" "$ROOT/spec/v3.json" "$OUT/v3.json"

gen() { # <dir> <generator> <additional-properties>
  rm -rf "${OUT:?}/$1"
  java -jar "$JAR" generate -i "$OUT/v3.json" -g "$2" -o "$OUT/$1" \
    --git-user-id Dockflow --git-repo-id dockflow-sdks --additional-properties "$3"
}

for lang in ${*:-typescript python csharp java php}; do
  case "$lang" in
    typescript) gen typescript typescript-fetch \
      "npmName=@dockflow/sdk,npmVersion=$VERSION,supportsES6=true,licenseName=MIT" ;;
    python) gen python python \
      "packageName=dockflow_sdk,projectName=dockflow-sdk,packageVersion=$VERSION,packageUrl=$REPO" ;;
    csharp) gen csharp csharp \
      "packageName=Dockflow.Sdk,packageVersion=$VERSION,packageDescription=Client for the Dockflow API v3,library=httpclient,targetFramework=netstandard2.0,packageCompany=Dockflow,packageAuthors=Dockflow,packageTitle=Dockflow API v3 SDK,licenseId=MIT,packageTags=dockflow container-tracking logistics" ;;
    java) gen java java \
      "groupId=com.dockflow,artifactId=dockflow-sdk,artifactVersion=$VERSION,invokerPackage=com.dockflow.sdk,apiPackage=com.dockflow.sdk.api,modelPackage=com.dockflow.sdk.model,library=native,artifactUrl=$REPO,artifactDescription=Dockflow API v3 SDK,developerName=Dockflow,developerEmail=sysadmin@dockflow.com,developerOrganization=Dockflow,developerOrganizationUrl=https://dockflow.com,scmConnection=scm:git:$REPO.git,scmDeveloperConnection=scm:git:$REPO.git,scmUrl=$REPO,licenseName=MIT,licenseUrl=https://opensource.org/licenses/MIT" ;;
    php) gen php php \
      "invokerPackage=Dockflow\\Sdk,composerPackageName=dockflow/dockflow-sdk,artifactVersion=$VERSION,licenseName=MIT" ;;
    *) echo "unknown language: $lang" >&2; exit 1 ;;
  esac
done
