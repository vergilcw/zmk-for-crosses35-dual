# Plan

Goal: a personal, reliable firmware for the Crosses 35 dual-trackball, with
the keymap codified in git, quality-of-life typing/pointing features, and
rock-solid BLE/USB. Status legend: `[x]` done, `[ ]` todo, `[~]` in progress.

## Inbox

New work discovered mid-task lands here; triage into a phase before ending a session.

- [ ] Decide whether to keep the Q+W → Esc combo (Base already has Esc on a thumb `&lt`).
- [ ] Review odd bindings carried over from Studio (see knowledge base, "Keymap oddities").

## Phase 0 — Foundations

- [x] AGENTS.md + docs/ knowledge base.
- [x] Export the live Studio keymap off the device (read-only RPC) → `docs/studio-snapshots/2026-10-10.json`.
- [x] Codify it in `config/crosses.keymap` (scripts/studio_to_keymap.py).
- [x] keymap-drawer config fixes + `draw-keymaps.yml` auto-render workflow; initial `keymap-drawer/crosses.svg`.
- [x] README rewrite (port relevant upstream zmk-for-crosses content).
- [ ] Dev-machine tooling (uv, python3, keymap-drawer, jq) — change staged in the user's NixOS
      config and builds; **user to deploy**.

## Phase 1 — Baseline build & flash

- [x] Push to `vergilcw/zmk-for-crosses35-dual` and confirm the CI build is green
      (2026-10-10, run 38101175564: left, right+Studio, settings_reset all built).
- [x] Confirm the draw workflow runs (run 38101175590 green; no commit needed — CI render matched the local one).
- [ ] Flash right (central, Studio) then left; follow `flashing.md`.
- [ ] In ZMK Studio run **Restore Stock Settings** so the firmware keymap (not stale Studio state) is live;
      re-verify with `scripts/studio_dump.py` that device == `config/crosses.keymap`.
- [ ] Pin floating west revisions (`cb-zmk-keebs@zephyr-4.1`, and its `main`-tracking imports) to commits
      for reproducible builds; record them in the knowledge base.
- [ ] Optional: local docker build path (`zmkfirmware/zmk-build-arm`) — root fs has ~8 GB free, so either
      relocate docker's data-root (system-config change) or stick with CI.

## Phase 2 — Typing accuracy & keymap cleanup

- [ ] Replace stock `&mt` on Base (Z, X, ., /, Bspc, Ret) with a tuned hold-tap ("home-row-mod" style):
      `flavor = "balanced"` or `"tap-preferred"`, `require-prior-idle-ms ≈ 150`, `quick-tap-ms ≈ 175`,
      `hold-trigger-key-positions` = opposite hand (+ thumbs), `hold-trigger-on-release`.
- [ ] Consider the same for `&lt LOWER M` (letter on a layer-tap is the same failure mode).
- [ ] Note: Studio can't edit hold-tap parameters; custom behaviors must live in the keymap file.
- [ ] Remove the easy-to-hit `&bt BT_CLR` on Raise (G position) — risk of accidental profile wipes.
- [ ] Bind `&kp F20` for mic mute. Linux xkb maps F20 → `XF86AudioMicMute` by default (*unverified on
      the dev machine*); otherwise add a GNOME custom shortcut via the system config. macOS: map in system settings / Karabiner.

## Phase 3 — Pointing features

- [ ] Sniper mode while Raise is held: child node on the right (central) trackball listener with
      `layers = <RAISE>` and `input-processors = <&zip_xy_scaler 1 4>` (tune divisor).
- [ ] Axis-locked scrolling (vertical-only / horizontal-only) for the left (scroll) trackball: layer-scoped
      scaler that zeroes `INPUT_REL_HWHEEL` or `INPUT_REL_WHEEL` on the central listener.
- [ ] Trackball angle: rotate pointer to match hand position — candidate module
      `efogdev/zmk-input-processor-rotate-plane` (`&zip_rotate_pointer { angle = <N>; }`). Measure angle per side.
- [ ] Trackball → volume / brightness on a layer: needs a motion→keypress input processor (research
      candidates); decide which ball and layer.
- [ ] Decide where overrides live: `config/crosses_{left,right}.overlay` (verify ZMK picks these up for split
      shields at our ZMK commit) vs. vendoring the shield into this repo.

## Phase 4 — Connectivity reliability (occasional "stops working until power-cycle")

Keyboard is mostly stable, so this comes after features; collect evidence opportunistically meanwhile.

- [ ] Characterise symptoms when they happen: USB vs BLE, which host/profile, after sleep/idle?, one half
      or both (split link vs host link)?, does the OLED still update?, do trackballs still work?
- [ ] Build a debug variant of the right half with the `zmk-usb-logging` snippet; capture logs at failure.
- [ ] Review suspect settings inherited from `cb-zmk-keebs` shield confs (see hardware.md) — e.g.
      `CONFIG_ZMK_BLE_EXPERIMENTAL_FEATURES`, `BT_PERIPHERAL_PREF_MAX_INT=6`, `BT_CTLR_TX_PWR_DYNAMIC_CONTROL`,
      `ZMK_BLE_MOUSE_REPORT_QUEUE_SIZE=1`, sleep vs `force-awake` trackballs, report-rate limiter.
      Compare with upstream zmk-for-crosses `crosses.conf` (larger BT buffers, `ZMK_BLE_EXPERIMENTAL_CONN`).
- [ ] Add explicit `&out OUT_USB` / `&out OUT_BLE` keys and `&sys_reset` / `&bootloader` on a safe layer so
      recovery doesn't require a power-cycle.
- [ ] Change one variable at a time; log each experiment + outcome in the knowledge base.

## Phase 5 — Extras

- [ ] Revisit OLED content, battery reporting, sleep timeout.

## Phase 6 — Polish

- [ ] README: per-layer explanation, feature list, badges stay green.
- [ ] Optional: release tagging of known-good firmware.
