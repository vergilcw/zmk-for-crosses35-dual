# Keymap workflow

`config/crosses.keymap` is the source of truth. ZMK Studio is for quick
experiments; anything worth keeping gets exported and codified here.

## Edit → render → build

1. Edit `config/crosses.keymap` (keep the grid aligned; use `BASE`/`LOWER`/`RAISE`/`MOUSE`).
2. Render locally (optional — CI does this on push):

   ```fish
   # from the repo root
   keymap -c keymap_drawer.config.yaml parse -z config/crosses.keymap > keymap-drawer/crosses.yaml
   keymap -c keymap_drawer.config.yaml draw keymap-drawer/crosses.yaml -j config/info.json > keymap-drawer/crosses.svg
   ```

   keymap-drawer fetches glyph SVGs from raw.githubusercontent.com, which is unreachable from the dev machine in
   agent sessions; see the knowledge base for the `gh api` cache-seeding workaround.
3. Push → `build.yml` builds firmware, `draw-keymaps.yml` re-renders and commits `keymap-drawer/crosses.{yaml,svg}`.
4. Flash (see flashing.md), then **Restore Stock Settings** in Studio if Studio edits were ever saved.

## Studio state overrides the firmware keymap

Studio saves edited layers to the right half's settings flash. Those survive re-flashing and win over
the compiled keymap. After flashing a keymap change, run *Restore Stock Settings* in ZMK Studio (or flash
`settings_reset` — but that also wipes BLE bonds) so the new firmware keymap is actually used.

## Exporting the live keymap from the device

Read-only; needs the right half on USB and unlocked (press `&studio_unlock`, Mouse layer → N position).

```fish
# from the repo root
env UV_PYTHON_DOWNLOADS=never uv run scripts/studio_dump.py --lock-only    # prints name + lock state
env UV_PYTHON_DOWNLOADS=never uv run scripts/studio_dump.py > /tmp/studio-dump.json
env UV_PYTHON_DOWNLOADS=never uv run scripts/studio_to_keymap.py /tmp/studio-dump.json
```

- `studio_dump.py` speaks the Studio RPC framing (SOF `0xAB` / ESC `0xAC` / EOF `0xAD`) using protobufs
  from `electronicmaterialsoffice/zmk-studio-cli` (pinned). It skips unsolicited notifications, which the
  upstream CLI doesn't (it printed nothing for `get-keymap`).
- `studio_to_keymap.py` maps behavior display names → ZMK syntax and HID usages → keycode names using the
  `keys.h` of the ZMK revision in `config/west.yml` (sparse-fetched into `.cache/zmk-headers/`).
  Unknown behaviors are emitted as `/* name p1 p2 */ &none` — check for those.
- `UV_PYTHON_DOWNLOADS=never` makes uv use nixpkgs' python3; uv-managed pythons don't run on NixOS.
- Save notable dumps to `docs/studio-snapshots/<date>.json`.
