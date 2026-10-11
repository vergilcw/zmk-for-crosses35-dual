#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""Convert a studio_dump.py JSON dump into ZMK devicetree binding rows.

Usage: uv run scripts/studio_to_keymap.py studio-dump.json [ZMK_DT_BINDINGS_DIR]

If ZMK_DT_BINDINGS_DIR (.../app/include/dt-bindings/zmk) is omitted, the
headers for the zmk revision pinned in config/west.yml are sparse-fetched
into <repo>/.cache/zmk-headers/<rev> (gitignored).

Builds a reverse lookup of HID usages from ZMK's keys.h so values like
0x0207001E render as LS(N1). Prints one `bindings = < ... >;` block per
layer, laid out for the 36-key (3x5+3) Crosses layout.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

MODS = [(0x01, "LC"), (0x02, "LS"), (0x04, "LA"), (0x08, "LG"),
        (0x10, "RC"), (0x20, "RS"), (0x40, "RA"), (0x80, "RG")]

# Preferred spellings when several keys.h aliases share a value.
PREFERRED = {
    "SEMI", "SQT", "BSPC", "RET", "ESC", "TAB", "SPACE", "DEL", "COMMA", "DOT",
    "FSLH", "BSLH", "MINUS", "EQUAL", "LBKT", "RBKT", "GRAVE", "HOME", "END",
    "PG_UP", "PG_DN", "LEFT", "RIGHT", "UP", "DOWN", "INS", "CAPS", "PSCRN",
    "LCTRL", "LSHFT", "LALT", "LGUI", "RCTRL", "RSHFT", "RALT", "RGUI",
    "C_PP", "C_NEXT", "C_PREV", "C_MUTE", "C_VOL_UP", "C_VOL_DN",
    "C_BRI_UP", "C_BRI_DN", "K_APP", "C_AC_BACK", "C_AC_FORWARD",
}


def load_names(hdr_dir: Path):
    defs = {}
    for f in ("hid_usage_pages.h", "hid_usage.h", "keys.h"):
        src = re.sub(r"\\\n\s*", " ", (hdr_dir / f).read_text())
        for line in src.splitlines():
            if "DEPRECATED" in line:
                continue
            m = re.match(r"#define\s+(\w+)\s+(.+?)\s*(//.*)?$", line)
            if m:
                defs[m.group(1)] = m.group(2)

    cache = {}

    def ev(name, depth=0):
        if name in cache:
            return cache[name]
        expr = defs[name]
        expr = re.sub(r"ZMK_HID_USAGE\(", "_U(", expr)
        for tok in sorted(set(re.findall(r"[A-Za-z_]\w*", expr)) - {"_U"}, key=len, reverse=True):
            if tok in defs:
                expr = re.sub(rf"\b{tok}\b", str(ev(tok, depth + 1)), expr)
        val = eval(expr, {"_U": lambda p, i: (p << 16) | i})  # noqa: S307 - trusted ZMK headers
        cache[name] = val
        return val

    by_val = {}
    keys_src = re.sub(r"\\\n\s*", " ", (hdr_dir / "keys.h").read_text())
    for name in re.findall(r"^#define\s+(\w+)\s", keys_src, re.M):
        if name not in defs:
            continue
        try:
            v = ev(name)
        except Exception:
            continue
        by_val.setdefault(v, []).append(name)

    def pick(names):
        pref = [n for n in names if n in PREFERRED]
        return pref[0] if pref else min(names, key=len)

    return {v: pick(ns) for v, ns in by_val.items()}


def keycode(val, names):
    mods, base = val >> 24, val & 0xFFFFFF
    s = names.get(base, hex(base))
    for bit, fn in reversed(MODS):
        if mods & bit:
            s = f"{fn}({s})"
    return s


def binding(b, behaviors, names):
    bid = b.get("behavior_id", 0)
    p1, p2 = b.get("param1", 0), b.get("param2", 0)
    name = behaviors.get(str(bid), {}).get("display_name", f"?{bid}")
    kc = lambda v: keycode(v, names)
    match name:
        case "Key Press": return f"&kp {kc(p1)}"
        case "Mod-Tap": return f"&mt {kc(p1)} {kc(p2)}"
        case "Layer-Tap": return f"&lt {p1} {kc(p2)}"
        case "Momentary Layer": return f"&mo {p1}"
        case "Toggle Layer": return f"&tog {p1}"
        case "To Layer": return f"&to {p1}"
        case "Sticky Layer": return f"&sl {p1}"
        case "Sticky Key": return f"&sk {kc(p1)}"
        case "Key Toggle": return f"&kt {kc(p1)}"
        case "Transparent": return "&trans"
        case "None": return "&none"
        case "Mouse Key Press":
            return "&mkp " + {1: "LCLK", 2: "RCLK", 4: "MCLK", 8: "MB4", 16: "MB5"}.get(p1, str(p1))
        case "Bluetooth":
            cmd = {0: "BT_CLR", 1: "BT_NXT", 2: "BT_PRV", 4: "BT_CLR_ALL"}.get(p1)
            if cmd:
                return f"&bt {cmd}"
            return f"&bt {'BT_SEL' if p1 == 3 else 'BT_DISC'} {p2}"
        case "Output Selection": return "&out " + {0: "OUT_TOG", 1: "OUT_USB", 2: "OUT_BLE"}[p1]
        case "Studio Unlock": return "&studio_unlock"
        case "Bootloader": return "&bootloader"
        case "Reset": return "&sys_reset"
        case "Caps Word": return "&caps_word"
        case "Key Repeat": return "&key_repeat"
        case "Grave/Escape": return "&gresc"
        case "auto_shift": return f"&as {kc(p1)} {kc(p2)}"
        case _: return f"/* {name} {p1} {p2} */ &none"


def fetch_headers() -> Path:
    west = (REPO / "config/west.yml").read_text()
    rev = re.search(r"- name: zmk\n(?:\s+\w+:.*\n)*?\s+revision:\s*(\S+)", west).group(1)
    dest = REPO / ".cache/zmk-headers" / rev
    hdrs = dest / "app/include/dt-bindings/zmk"
    if not (hdrs / "keys.h").exists():
        dest.mkdir(parents=True, exist_ok=True)
        git = lambda *a: subprocess.run(["git", "-C", str(dest), *a], check=True, capture_output=True)
        git("init", "-q")
        git("fetch", "-q", "--depth", "1", "--filter=blob:none", "https://github.com/zmkfirmware/zmk", rev)
        git("checkout", "-q", "FETCH_HEAD", "--", "app/include/dt-bindings/zmk")
    return hdrs


def main():
    dump = json.loads(Path(sys.argv[1]).read_text())
    names = load_names(Path(sys.argv[2]) if len(sys.argv) > 2 else fetch_headers())
    beh = dump["behaviors"]
    rows = [(0, 10), (10, 20), (20, 30), (30, 36)]
    for i, layer in enumerate(dump["keymap"]["layers"]):
        cells = [binding(b, beh, names) for b in layer["bindings"][:36]]
        widths = [max(len(cells[r0 + c]) for r0, r1 in rows[:3]) for c in range(10)]
        print(f"        layer_{i} {{\n            display-name = \"{layer.get('name', '')}\";\n            bindings = <")
        for r0, r1 in rows[:3]:
            print("  ".join(cells[r0 + c].ljust(widths[c]) for c in range(10)).rstrip())
        thumbs = cells[30:36]
        print(" " * (sum(widths[:2]) + 4) + "  ".join(t.ljust(widths[2 + j]) for j, t in enumerate(thumbs)).rstrip())
        print("            >;\n        };\n")


if __name__ == "__main__":
    main()
