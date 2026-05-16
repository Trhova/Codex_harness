#!/usr/bin/env bash
set -euo pipefail

environment="${1:?usage: smoke_test.sh <environment>}"
source "configs/${environment}.env"

curl --fail --silent --show-error "${PUBLIC_HOST}/healthz"
curl --fail --silent --show-error "${PUBLIC_HOST}/version" | grep -E '"git_sha":"[0-9a-f]{40}"'

echo "smoke tests passed for ${environment}"
