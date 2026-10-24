# Knowledge base

Dated, evidence-backed findings. Mark anything not directly verified as *unverified*.
Newest entries go at the top of each section.

## Right trackball port from Crosses 36 (2026-10-24)

- Reference repo behaviour: pointer on Base/Mouse, scroll on Lower, snipe (¼) on Raise, rotated 45° CCW. There it is
  done in a vendored DoctorWangWang driver; this repo uses efogdev's `pixart,pmw3610-efogtech` driver, which has no
  rotation/layer modes, so it is done with ZMK input processors instead (all in `config/crosses.keymap`).
- Chain: `trackball_central_listener` (shield; we override its `input-processors` to `<&zip_rotate_pointer>`) →
  rotate-plane processor device → our `rotated_pointer_listener` (`device = <&zip_rotate_pointer>`) whose base chain is
  the rate limiter and whose `layers` children override it: `lower_scroll` (`zip_xy_to_scroll_mapper`,
  `zip_scroll_scaler 1 2`) and `raise_snipe` (`zip_xy_scaler 1 4`). A matching child replaces the base chain, so each
  child repeats `zip_ble_report_rate_limit`.
- Module: `efogdev/zmk-input-processor-rotate-plane` pinned to `86901be` in `config/west.yml`; self-contained
  (`zmk_runtime_config` is optional, `ZRC_GET` falls back to the Kconfig default). It buffers X/Y until both arrive or
  1 ms elapses, rotates in float with remainders. An angle saved via its shell (`plane set`) persists in flash and would
  override the DT value — *unverified* whether any is stored (none was ever set).
- **Sign:** the module computes `x' = x·cos a − y·sin a`, the same matrix as the 36 repo's driver with
  `ROTATION_DEG = −a`. So `angle = <45>` here ≙ `CONFIG_PMW3610_ROTATION_DEG=-45` there. The base orientation here is
  `xy-swap` only (the 36 board uses `ORIENTATION_270` + `INVERT_X`), so *unverified on hardware* that the same sign
  gives "roll toward 10:30 → straight up". If it tilts the wrong way, change to `-45`.
- Scroll scaler `1 2` was copied from the left ball (CPI 600); the right ball is CPI 800 so it scrolls a bit faster,
  and direction (no `y-invert`) is *unverified*. Snipe ¼ matches the reference's 400/1600 CPI ratio.
- Verification: `scripts/local_build.sh` (zmk-build-arm:4.1) built both halves; right `zephyr.dts` contains
  `zip_rotate_pointer { angle = <0x2d>; }`, the listener children with layers 1/2, and `.config` has
  `CONFIG_ZMK_INPUT_PROCESSOR_ROTATE_PLANE=y`. Left half also builds (the rotate node and listener are
  present but idle there; `trackball_central_listener` is disabled on the left).
- `;` / `'`: the reference swapped them (`'` on an outer pinky key). Decision (user, 2026-10-24): not ported — this
  board has no outer column and `'` stays on the Base right pinky; `;` stays on the Mouse layer only. The 36 repo may
  be updated to match.
- Local docker build: `zmkfirmware/zmk-build-arm:4.1` (matches the ZMK workflow); `:stable` is the wrong Zephyr.
  Workspace ≈ 5 GB; `/` had 8 GB free afterwards.

## Left trackball: rotation and axis-locked scroll (2026-10-24)

- Before this, the left ball was **not rotated** (peripheral ran `xy_to_scroll_mapper` + `zip_scroll_scaler 1 2`; no angle
  anywhere). Now: peripheral sends raw X/Y; central rotates by `angle = <(-45)>` (custom `zip_rotate_left`, device-name
  `left`) — the mirror of the right ball's +45 (user's "+45" convention = clockwise = module −45) — then
  `left_ball_listener` locks the axis by layer (see hardware.md). Layer state exists only on the central, which is why
  the work moved off the peripheral. **Both halves must be flashed** for this change.
- Axis lock: `zip_x_scaler 0 1` zeroes X before the mapper (vertical only); `zip_y_scaler 0 1` for horizontal; the
  child node's `layers = <LOWER RAISE>` replaces the base chain. Compiled OK (local build, both halves).
- *Unverified on hardware:* rotation sign for the left ball, horizontal scroll direction, and that BLE carries the raw
  X/Y fast enough (the peripheral still rate-limits via `zip_ble_report_rate_limit`).

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
- **Combos are not visible over Studio RPC.** The Q+W→Esc combo was removed from the keymap on 2026-10-24; the
  device keeps the old one until flashed.

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
