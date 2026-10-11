# Building & flashing

> Agents: flashing needs an explicit go-ahead from the user every time.

## Get firmware

CI (`.github/workflows/build.yml`) runs on every push/PR and on manual dispatch:

```fish
gh workflow run build.yml -R vergilcw/zmk-for-crosses35-dual
gh run watch -R vergilcw/zmk-for-crosses35-dual
gh run download -R vergilcw/zmk-for-crosses35-dual -D /tmp/crosses-fw
```

Artifacts: `crosses_35_right.uf2` (central + Studio), `crosses_35_left.uf2`,
`settings_reset-nice_nano-zmk.uf2` (name may vary).

## Flash a half

1. Plug **one** half in over USB.
2. Double-tap its reset button → a `NICENANO` USB drive mounts.
3. Copy the matching `.uf2` onto it; it reboots and unmounts by itself (a "copy failed" error at the end is normal).

   ```fish
   cp /tmp/crosses-fw/crosses_35_right/*.uf2 /run/media/$USER/NICENANO/
   ```

4. Repeat for the other half. Flash **both** halves when the split protocol or shared config changes;
   keymap-only changes need only the right (central) half.

## After flashing

- If Studio edits were ever saved: ZMK Studio → *Restore Stock Settings* (keymap only; keeps bonds).
- Verify: `uv run scripts/studio_dump.py` and diff against the keymap (see keymap-workflow.md).

## Full reset (pairing broken, halves won't connect)

1. Flash `settings_reset` to **both** halves (wipes bonds + Studio keymap).
2. Re-flash `crosses_35_left` and `crosses_35_right`.
3. Power both on together so they re-pair; then remove "Crosses BT" from each host's Bluetooth list and re-pair.
