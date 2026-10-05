#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${GOTENBERG_URL:=http://localhost:3555}"
mkdir -p out
curl --fail --silent --show-error \
  -X POST "${GOTENBERG_URL%/}/forms/chromium/convert/html" \
  -F 'files=@index.html' \
  -o out/strands-decider-vs-jev.pdf
printf 'Wrote %s\n' "$PWD/out/strands-decider-vs-jev.pdf"
