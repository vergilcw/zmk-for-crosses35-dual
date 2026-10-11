# Knowledge base

Dated, evidence-backed findings. Mark anything not directly verified as *unverified*.
Newest entries go at the top of each section.

## Device & Studio RPC

- **2026-10-10** — Right half enumerates as `/dev/ttyACM0`
  (`/dev/serial/by-id/usb-ZMK_Project_Crosses_BT_<serial>-if00`), name `Crosses BT`.
  The user is in the `dialout` group, so no sudo needed.
- **2026-10-10** — Device reports Studio lock state `LOCKED` after boot even though the shield sets
  `CONFIG_ZMK_STUDIO_LOCKING=n`; pressing `&studio_unlock` (Mouse layer, N position) unlocks it.
  Keymap RPCs fail while locked. *(Why locking is still active is unverified — the user conf/build flags may win.)*
- **2026-10-10** — `zmk-studio-cli` (electronicmaterialsoffice, commit `3b3bce0`) reads only the first frame
  after a request, so `keymap get-keymap` printed nothing (a notification arrived first). Our
  `scripts/studio_dump.py` loops past notifications and matches `request_id`.
- **2026-10-10** — Studio keymap had 54 binding slots per layer (largest physical layout), active layout
  index 2 = "36 Key"; the first 36 slots map 1:1 to `config/crosses.keymap` order. Slots 36–53 are empty.
- **2026-10-10** — Behavior IDs on this firmware (from `list_all_behaviors`): 1 Mouse Key Press, 2 mouse_move,
  3 mouse_scroll, 4 None, 5 Key Press, 6 auto_shift (custom `&as`), 7 Bootloader, 8 Caps Word,
  9 External Power, 10 Grave/Escape, 11 Key Repeat, 12 Key Toggle, 13 Mod-Tap, 14 Output Selection,
  15 Polling rate (`rrl` from the shield), 16 Sticky Key, 17 Momentary Layer, 18 Sticky Layer, 19 Reset,
  20 To Layer, 21 Toggle Layer, 22 Bluetooth, 23 Layer-Tap, 24 Studio Unlock, 25 Transparent.
  IDs are firmware-specific; the converter maps by display name.
- **2026-10-10** — HID usage encoding in Studio params: `(implicit_mods << 24) | (page << 16) | id`;
  e.g. `0x0207001E` = `LS(N1)`.
- **Combos are not visible over Studio RPC** — the Q+W→Esc combo can't be confirmed on-device; it's kept
  because it was in the firmware source this device was built from.

## Keymap oddities (carried over verbatim from Studio, 2026-10-10)

Kept as-is so the codified keymap matches the device; review in Phase 2.

- Base: stock `&mt` (hold-preferred, 200 ms) on Z/X/./`/` and thumbs — the likely cause of missed letters
  when typing fast.
- Lower: top row starts `LS(N1)` (`!`) and ends `LS(N5)` (`%`) around Home/Up/End; middle row `N1` … `N5`;
  F-key block is `F1 F2 F3 F4 / F4 F5 F7 F11 / F1 F2 F3 F12` (duplicates, no F6/F8/F9/F10).
- Raise: `LS(KP_PLUS)` (shifted keypad plus) for `+`; `LS(C_PP)` / `LS(C_NEXT)` (shift + media keys);
  `&bt BT_CLR` on the G position.
- Mouse: BT profiles 0–4 on the outer left columns; Home/arrows/End duplicated from Lower.

## Tooling & environment (dev machine, NixOS)

- **2026-10-10** — No python/node on PATH by default; use `nix shell nixpkgs#python3 nixpkgs#uv -c …` until
  the system-config change (uv, python3, keymap-drawer, jq) is deployed. uv-managed Python downloads fail on
  NixOS (stub-ld) — set `UV_PYTHON_DOWNLOADS=never`.
- **2026-10-10** — `raw.githubusercontent.com` is unreachable from agent sessions on the dev machine (curl → 000),
  but `gh api` works. keymap-drawer glyphs can be pre-seeded into
  `$XDG_CACHE_HOME/keymap-drawer/glyphs/mdi:<name>.svg` from
  `gh api repos/Templarian/MaterialDesign-SVG/contents/svg/<name>.svg --jq .content | base64 -d`.
  Point `XDG_CACHE_HOME` at the repo's `.cache/` **only for the keymap binary**, not `nix shell` (nix would
  dump ~70 MB of its own cache there).
- **2026-10-10** — `rsvg-convert` drops text in keymap-drawer SVGs and `resvg` drops glyph `<use>`s; the SVG
  itself is fine (GitHub/browsers render both). Use a browser to eyeball renders.
- **2026-10-10** — keymap-drawer can't combine glyph modifiers with keys (`$$mdi:…$$+$$mdi:…$$` fails to
  fetch); `modifier_fn_map` uses plain-text `⇧` and common shifted symbols are in `raw_binding_map`.
- **2026-10-10** — Docker 29 available (user in `docker` group) but `/` has ~8 GB free and no ZMK images
  pulled; CI is the default build path.

## Upstream relationships

- `upstream` remote = `HeeTuic/zmk-for-crosses35-dual`; its CI was green (last runs ~June 2026) with the same
  `build.yaml` (`board: nice_nano`, Studio on right).
- `HeeTuic/zmk-for-crosses` (single-trackball, branch `35`) is the source of the README content, the
  keymap-drawer workflow, and a different BLE tuning in `config/crosses.conf` (bigger BT buffers,
  `ZMK_BLE_EXPERIMENTAL_CONN`, `BT_PERIPHERAL_PREF_MAX_INT=9`, latency 2) — useful comparison for Phase 4.

## Decision log

- **2026-10-10** — Keymap exported from Studio and codified verbatim (no "fixes") so the first flash is a
  no-op for typing behaviour; changes come in later phases.
- **2026-10-10** — Phase order: features (typing, pointing) before connectivity work; the keyboard is
  stable enough day-to-day (user decision).
- **2026-10-10** — ZMK tooling installed system-wide via the user's NixOS config rather than a repo devShell
  (user decision).
