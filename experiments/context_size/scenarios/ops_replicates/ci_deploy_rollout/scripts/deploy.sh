#!/usr/bin/env bash
set -euo pipefail

environment="${1:?usage: deploy.sh <environment> <image>}"
image="${2:?usage: deploy.sh <environment> <image>}"

config="configs/${environment}.env"
if [[ ! -f "${config}" ]]; then
  echo "unknown environment ${environment}" >&2
  exit 2
fi

source "${config}"

tmp_manifest="$(mktemp)"
trap 'rm -f "${tmp_manifest}"' EXIT

sed "s|IMAGE_PLACEHOLDER|${image}|g" k8s/deployment.yaml > "${tmp_manifest}"

kubectl -n "${NAMESPACE}" apply -f "${tmp_manifest}"
kubectl -n "${NAMESPACE}" scale deployment "${DEPLOYMENT}" --replicas="${REPLICAS}"
kubectl -n "${NAMESPACE}" rollout status "deployment/${DEPLOYMENT}" --timeout="${ROLLOUT_TIMEOUT}"
kubectl -n "${NAMESPACE}" annotate deployment "${DEPLOYMENT}" "deploy.image=${image}" --overwrite
