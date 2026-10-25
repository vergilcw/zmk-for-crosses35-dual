# Agent Instructions for zmk-for-crosses35-dual

Single, tool-agnostic instructions file (Copilot CLI, Codex, Gemini CLI and
Claude Code all read `AGENTS.md`). Don't create `CLAUDE.md`/`GEMINI.md`.

## Context

ZMK firmware config for @vergilcw's **Crosses 35 dual-trackball** wireless
split keyboard (3x5+3, two nice!nano v2 controllers, two PMW3610 trackballs,
two 128x32 OLEDs). Forked from
[HeeTuic/zmk-for-crosses35-dual](https://github.com/HeeTuic/zmk-for-crosses35-dual)
(remote `upstream`); the shield/board definition is **not in this repo** — it
comes from `HeeTuic/cb-zmk-keebs@zephyr-4.1` via `config/west.yml`.
The PCB is modified, so pinouts differ from the original GGGW Crosses.

Start with [`docs/README.md`](docs/README.md) (index), then
[`docs/plan.md`](docs/plan.md) (roadmap/status) and
[`docs/knowledge-base.md`](docs/knowledge-base.md) (verified findings and
gotchas). Trust those docs over re-deriving everything, but verify anything
marked *unverified*.

## Repo map

| Path | What |
| --- | --- |
| `config/crosses.keymap` | The keymap (source of truth). Layers: Base, Lower, Raise, Mouse. |
| `config/crosses.conf` | User Kconfig overrides (applies to both halves). |
| `config/west.yml` | West manifest: pinned ZMK + `cb-zmk-keebs` (shield, drivers). |
| `config/info.json` | QMK-style physical layout used by keymap-drawer. |
| `build.yaml` | CI build matrix (left, right+Studio, settings_reset). |
| `.github/workflows/build.yml` | Firmware build (ZMK reusable workflow). |
| `.github/workflows/draw-keymaps.yml` | Renders `keymap-drawer/crosses.svg` and commits it. |
| `keymap_drawer.config.yaml` | keymap-drawer styling/legend config. |
| `scripts/` | Studio keymap export tools (see `docs/keymap-workflow.md`). |
| `docs/` | Plan, knowledge base, how-tos. Keep in sync with code. |

## Approval boundaries (hard rules)

Ask for an explicit in-conversation go-ahead before:

- **Flashing** either half, or anything that enters the bootloader / copies a
  `.uf2`. Flash order and recovery steps are in `docs/flashing.md`.
- **Writing to the keyboard over ZMK Studio RPC** (set/save/discard/reset,
  layer add/remove). Read-only `get_*`/`list`/`check` calls are fine, but the
  user must press `&studio_unlock` themselves; ask them to.
- Pushing to any remote, opening PRs, or changing GitHub repo settings.
- Destructive git (force-push, history rewrite, `reset --hard` on unpushed work).
- Changing the user's system (NixOS) config beyond proposing a diff — the user deploys it.

Safe without asking: editing files in this repo, local renders
(keymap-drawer), offline script runs against saved dumps, `gh` read-only
queries, local docker builds (mind disk space, see knowledge base).

## Working conventions

- **Paths:** use absolute paths inside the repo checkout
  or `/tmp`. Never use `..` in paths; the user's permission policy rejects it.
  Keep caches inside the repo's gitignored `.cache/` rather than `~/.cache`.
- **Shell:** the user's shell is fish. Commands you suggest for them to run must
  be fish-compatible (`set -x VAR value`, no `VAR=value cmd`; use `env VAR=value cmd`).
- **Tooling on the dev machine (NixOS):** `uv`, `python3`, `keymap-drawer`, `jq` come from
  the user's system config. If missing, use
  `nix shell nixpkgs#<pkg> -c ...`. Don't set `XDG_CACHE_HOME` around `nix`
  itself (it spills nix's cache into the repo).
- **Keymap edits:** keep the 10/10/10/6 grid alignment, use the layer
  `#define`s (`BASE`, `LOWER`, `RAISE`, `MOUSE`), and after editing re-render
  with keymap-drawer (CI does it on push too).
- **ZMK version:** ZMK is pinned to a commit on `main` (Zephyr 4.1 era). Check
  docs for that era, not the v0.3 docs, when using newer features
  (input processors, physical layouts, Studio).
- **Commits:** small, descriptive; include the Copilot co-author trailer.
- **Before pushing:** run `git fetch` and check `git log HEAD..origin/main`. The draw workflow
  commits `keymap-drawer/crosses.{svg,yaml}` to `main` after every push, so the next push is usually rejected
  as non-fast-forward. If it is, `git rebase -X theirs origin/main` (in a rebase "theirs" is *your* commit, so
  your freshly rendered diagram wins and CI redraws it anyway), then push. Never force-push.

## Documentation stays in sync

When you change behavior, config, workflow, or learn something non-obvious:

- Update `docs/plan.md` status (check items off immediately; add new work to
  its Inbox section rather than derailing the current task).
- Record verified facts and gotchas in `docs/knowledge-base.md` with a date and
  evidence (file:line, command output, or link). Mark guesses *unverified*.
- Update `README.md` when user-facing layout/features change.
