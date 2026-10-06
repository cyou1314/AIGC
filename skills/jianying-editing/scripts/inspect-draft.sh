#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /absolute/path/to/jianying-draft" >&2
  exit 64
fi

project=$1

if [ ! -d "$project" ]; then
  echo "Draft directory not found: $project" >&2
  exit 66
fi

if ! command -v capcut >/dev/null 2>&1; then
  echo "capcut CLI is not on PATH" >&2
  exit 69
fi

echo "== tool doctor =="
capcut doctor -H
echo "== version =="
capcut version "$project" -H
echo "== diagnose =="
capcut diagnose "$project" -H
echo "== project overview =="
capcut info "$project" -H
