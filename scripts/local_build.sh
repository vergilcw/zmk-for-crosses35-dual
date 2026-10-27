#!/usr/bin/env bash
# Local ZMK build in docker (mirrors build.yaml). Workspace: .west-workspace/ (gitignored, ~5 GB).
# Usage: scripts/local_build.sh [right|left|both]   -> .west-workspace/build/<half>/zephyr/zmk.uf2
set -euo pipefail
repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
halves=${1:-both}
mkdir -p "$repo/.west-workspace"
rm -rf "$repo/.west-workspace/config" && cp -r "$repo/config" "$repo/.west-workspace/config"
docker run --rm -v "$repo/.west-workspace:/ws" -e HALVES="$halves" zmkfirmware/zmk-build-arm:4.1 bash -ec '
  cd /ws
  [ -d .west ] || west init -l config
  west update --fetch-opt=--filter=tree:0
  west zephyr-export >/dev/null
  [ "$HALVES" = both ] && HALVES="right left"
  for half in $HALVES; do
    extra=""
    [ "$half" = right ] && extra="-DSNIPPET=studio-rpc-usb-uart -DCONFIG_ZMK_STUDIO=y"
    west build -p always -s zmk/app -d build/$half -b nice_nano -- -DSHIELD=crosses_$half -DZMK_CONFIG=/ws/config $extra > build_$half.log 2>&1 \
      || { tail -40 build_$half.log; exit 1; }
    echo "$half OK -> build/$half/zephyr/zmk.uf2"
  done'
