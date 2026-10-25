# Plan

Goal: a personal, reliable firmware for the Crosses 35 dual-trackball, with
the keymap codified in git, quality-of-life typing/pointing features, and
rock-solid BLE/USB. Status legend: `[x]` done, `[ ]` todo, `[~]` in progress.

## Inbox

New work discovered mid-task lands here; triage into a phase before ending a session.

- [ ] Flash the 2026-10-24 port build (rotation/scroll/snipe/`;`) and tune: rotation sign, Lower scroll
      speed/direction (`zip_scroll_scaler 1 2` is copied from the left ball, unverified for the right) — see
      knowledge base "Right trackball port".
- [ ] Pin the remaining floating west revisions (`cb-zmk-keebs@zephyr-4.1`, `efogdev/zmk-pmw3610-driver`,
      `zmk-report-rate-limit`, `zmk-input-processor-xyz`); a driver update could silently change pointer feel.
- [x] Q+W → Esc combo dropped (2026-10-24, matches the Crosses 36 repo; Esc is on the Esc/Lower thumb).
- [ ] Review odd bindings carried over from Studio (see knowledge base, "Keymap oddities").

## Port from Crosses 36 (2026-10-24)

Reference: `/home/vergilcw/zmk-for-crosses` branch `36` (`docs/plan.md`, `docs/knowledge-base.md`). Goal: same keymap
and right-trackball behaviour minus the outer pinky columns and the second ball.

- [-] `;`/`'` swap skipped (user, 2026-10-24): `'` stays on the Base right pinky; `;` stays on Mouse. The 36 repo may be changed to match later.
- [x] Q+W combo and unused `&as` behavior removed.
- [x] Right ball: rotate 45° CCW, Lower = scroll, Raise = snipe, Base/Mouse = pointer (keymap file).
- [x] Local docker build of both halves compiles; devicetree checked (knowledge base).
- [x] Right half flashed 2026-10-24 with the first port build (run 40129987723); user: "looks right".
- [x] Layer scheme revision (LMouse on `V`, RMouse on `M` — swapped 2026-10-25 to LMouse on `C`, RMouse on `,`, with Lower on `V`/`M`; Lower = unrotated vertical scroll on both balls,
      layer-taps on `C`/`,`, left ball horizontal scroll on Raise): compiled locally, committed.
- [ ] Push (**ask first**), confirm CI, flash **both** halves (**ask first**), tune (scroll directions, angles).
- [ ] Later: tune hold-taps (`&lt` on C/V/M/comma, `&mt`s), per user "revisit later".
- [ ] Port the same scheme to the unibody boards / update the Crosses 36 repo (`'` placement, Lower unrotated scroll).

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
- [x] Local docker build path: `scripts/local_build.sh` (image `zmk-build-arm:4.1`; ~5 GB in `.west-workspace/`).

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

- [x] Sniper mode while Raise is held: `raise_snipe` child of `rotated_pointer_listener` (`zip_xy_scaler 1 4`).
      Built, not yet flashed/tuned (2026-10-24).
- [x] Scroll on the right ball while Lower is held (ported from the Crosses 36 repo).
- [ ] Axis-locked scrolling (vertical-only / horizontal-only) for the left (scroll) trackball: layer-scoped
      scaler that zeroes `INPUT_REL_HWHEEL` or `INPUT_REL_WHEEL` on the central listener.
- [x] Trackball angle on the right ball: `efogdev/zmk-input-processor-rotate-plane` at 45° (= "−45° CCW" of the
      Crosses 36 repo). Built, not yet flashed. [ ] Left ball rotation/scroll done in the 2026-10-24 layer scheme (see below), awaiting flash/test of both halves.
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
