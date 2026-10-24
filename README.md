# Crosses 35 Dual — vergilcw's ZMK config

![ZMK Build](https://img.shields.io/github/actions/workflow/status/vergilcw/zmk-for-crosses35-dual/build.yml?branch=main&label=ZMK%20Build&style=for-the-badge&color=2ac3de) ![Keymap Draw](https://img.shields.io/github/actions/workflow/status/vergilcw/zmk-for-crosses35-dual/draw-keymaps.yml?branch=main&label=Keymap%20Draw&style=for-the-badge&color=bb9af7)

Personal [ZMK](https://zmk.dev) firmware for a **wireless Crosses 35 split keyboard with two trackballs**
(3×5+3 keys, nice!nano v2 controllers, PMW3610 sensors, 128×32 OLEDs). Forked from
[HeeTuic/zmk-for-crosses35-dual](https://github.com/HeeTuic/zmk-for-crosses35-dual).

> ⚠️ Only for the **MIAOMIAO / HeeTuic modified-PCB** Crosses 35 dual-trackball. Pinouts differ from the
> original [GGGW Crosses](https://github.com/Good-Great-Grand-Wonderful/crosses); don't flash this on other boards.

- **Right half** — central: connects to the computer over USB/Bluetooth, runs ZMK Studio, trackball = pointer
  (scroll on Lower, slow "snipe" on Raise, rotated 45° counterclockwise).
- **Left half** — peripheral: trackball = scroll wheel.

---

## 🗺️ Keymap

![Crosses keymap](keymap-drawer/crosses.svg)

*Rendered by [keymap-drawer](https://github.com/caksoylar/keymap-drawer) via GitHub Actions on every change to
`config/crosses.keymap` — always matches the firmware source.*

| Layer | Reach | What's there |
| --- | --- | --- |
| **Base** | — | QWERTY, `'` on the right pinky, mod-taps on the bottom row (Alt/Shift on Z X . /), thumbs: Tab/Mouse · Bspc/Shift · Esc/Lower — Ret/Ctrl · Space/Raise · Gui |
| **Lower** | hold left-inner thumb or M | Navigation (Home/arrows/End), media + brightness, F-keys, mouse buttons on right thumbs, USB/BT toggle. **Right trackball scrolls.** |
| **Raise** | hold right-middle thumb | Symbols on the left, numpad on the right, media prev/next. **Right trackball in slow snipe mode.** |
| **Mouse** | hold left-outer thumb | Bluetooth profiles 0–4, mouse buttons, brackets/parens, Studio unlock |

The keymap mirrors my [Crosses 36](https://github.com/vergilcw/zmk-for-crosses36) (single-trackball) board's inner
block, minus its outer pinky columns. Trackball rotation/layer behaviour is in the keymap file
(see [docs/hardware.md](docs/hardware.md)); the left ball is always a scroll wheel.

---

## 🛠️ Changing the keymap

### Source of truth: `config/crosses.keymap`
Edit, push, and GitHub Actions builds the firmware and redraws the diagram above. See
[docs/keymap-workflow.md](docs/keymap-workflow.md).

### ZMK Studio (live remapping, no flashing)
Open [zmk.studio](https://zmk.studio/) in a Chromium browser (or the desktop app), connect the **right half** over
USB, press **Studio unlock** (Mouse layer → N). Changes apply instantly and are saved on the keyboard.

> Studio-saved layers override the compiled keymap, even after re-flashing. Codify anything you want to keep
> (`scripts/studio_dump.py` exports the live keymap) and use *Restore Stock Settings* after flashing.

### Keymap Editor (web GUI that commits to GitHub)
[Keymap Editor](https://nickcoutsos.github.io/keymap-editor/) can edit `config/crosses.keymap` — including
combos, macros and hold-tap behaviors — and commits straight to this repo, triggering a build.

---

## 🚀 Flashing

Full guide: [docs/flashing.md](docs/flashing.md).

1. Open the latest successful **Build ZMK firmware** run under *Actions* and download the `firmware` artifact
   (or `gh run download`).
2. Plug in **one** half, double-tap its reset button — a `NICENANO` drive appears.
3. Copy `crosses_35_right.uf2` / `crosses_35_left.uf2` to the matching half. It reboots when done.
4. Keymap-only changes need just the right half. If halves stop pairing, flash `settings_reset` to both, then
   re-flash both.

---

## 📚 Project docs

- [docs/plan.md](docs/plan.md) — roadmap and status (typing fixes, axis-locked scrolling, mic-mute key,
  connectivity hardening)
- [docs/hardware.md](docs/hardware.md) — how the halves, trackballs and ZMK modules fit together
- [docs/knowledge-base.md](docs/knowledge-base.md) — findings, gotchas, decisions
- [AGENTS.md](AGENTS.md) — instructions for AI coding agents working in this repo

---

## 🙏 Credits

- [HeeTuic](https://github.com/HeeTuic) — modified Crosses PCB, original firmware
  ([zmk-for-crosses35-dual](https://github.com/HeeTuic/zmk-for-crosses35-dual),
  [zmk-for-crosses](https://github.com/HeeTuic/zmk-for-crosses), [cb-zmk-keebs](https://github.com/HeeTuic/cb-zmk-keebs))
- [Good-Great-Grand-Wonderful](https://github.com/Good-Great-Grand-Wonderful/crosses) — Crosses design
- [efogdev](https://github.com/efogdev) (PMW3610 driver, report-rate limit), [badjeff](https://github.com/badjeff),
  [caksoylar](https://github.com/caksoylar) (keymap-drawer), and the [ZMK](https://github.com/zmkfirmware/zmk) project
