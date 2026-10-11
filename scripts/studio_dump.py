#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pyserial>=3.5",
#   "protobuf>=6.33,<7",
#   "zmk-studio-cli @ git+https://github.com/electronicmaterialsoffice/zmk-studio-cli@3b3bce06230e497905ab22b343ca866081aa2b07",
# ]
# ///
"""Dump the live keymap from a ZMK Studio-enabled keyboard over USB serial to JSON.

Read-only: only issues get_*/list/check requests, never set/save. Keymap
requests need the keyboard unlocked (press &studio_unlock) first. Uses the
protobuf bindings shipped with
https://github.com/electronicmaterialsoffice/zmk-studio-cli.

Usage: uv run scripts/studio_dump.py [--lock-only] [/dev/ttyACM0] > /tmp/studio-dump.json
"""

import json
import sys

import serial
from google.protobuf.json_format import MessageToDict
from zmk_studio_cli.proto import core_pb2
from zmk_studio_cli.proto import studio_pb2 as studio

SOF, ESC, EOF = 0xAB, 0xAC, 0xAD


class Studio:
    def __init__(self, port):
        self.ser = serial.Serial(port, timeout=3)
        self.ser.reset_input_buffer()
        self.next_id = 1

    def _send(self, req):
        out = bytearray([SOF])
        for b in req.SerializeToString():
            if b in (SOF, ESC, EOF):
                out.append(ESC)
            out.append(b)
        out.append(EOF)
        self.ser.write(out)

    def _read_frame(self):
        while True:
            c = self.ser.read(1)
            if not c:
                raise TimeoutError("no response from keyboard")
            if c[0] == SOF:
                break
        buf = bytearray()
        while True:
            c = self.ser.read(1)
            if not c:
                raise TimeoutError("truncated frame")
            if c[0] == ESC:
                buf += self.ser.read(1)
            elif c[0] == EOF:
                return bytes(buf)
            else:
                buf += c

    def call(self, fill):
        req = studio.Request()
        req.request_id = self.next_id
        self.next_id += 1
        fill(req)
        self._send(req)
        # Skip unsolicited notifications (e.g. lock-state changes) until our reply arrives.
        while True:
            resp = studio.Response()
            resp.ParseFromString(self._read_frame())
            if resp.WhichOneof("type") != "request_response":
                continue
            rr = resp.request_response
            if rr.request_id != req.request_id:
                continue
            if rr.WhichOneof("subsystem") == "meta":
                raise RuntimeError(f"RPC error: {rr.meta} (is the keyboard unlocked?)")
            return rr


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    s = Studio(args[0] if args else "/dev/ttyACM0")
    d = lambda m: MessageToDict(m, preserving_proto_field_name=True)

    info = s.call(lambda r: setattr(r.core, "get_device_info", True)).core.get_device_info
    lock = core_pb2.LockState.Name(
        s.call(lambda r: setattr(r.core, "get_lock_state", True)).core.get_lock_state
    )
    if "--lock-only" in sys.argv:
        print(info.name, lock)
        return

    beh_ids = s.call(lambda r: setattr(r.behaviors, "list_all_behaviors", True)).behaviors.list_all_behaviors.behaviors
    behaviors = {}
    for bid in beh_ids:
        det = s.call(lambda r, b=bid: setattr(r.behaviors.get_behavior_details, "behavior_id", b))
        behaviors[bid] = d(det.behaviors.get_behavior_details)
    keymap = s.call(lambda r: setattr(r.keymap, "get_keymap", True)).keymap.get_keymap
    layouts = s.call(lambda r: setattr(r.keymap, "get_physical_layouts", True)).keymap.get_physical_layouts
    unsaved = s.call(lambda r: setattr(r.keymap, "check_unsaved_changes", True)).keymap.check_unsaved_changes

    json.dump(
        {
            # Serial is the chip's unique ID; omitted so dumps are safe to commit.
            "device": {"name": info.name},
            "lock_state": lock,
            "unsaved_changes": unsaved,
            "behaviors": behaviors,
            "keymap": d(keymap),
            "physical_layouts": d(layouts),
        },
        sys.stdout,
        indent=2,
    )
    print()


if __name__ == "__main__":
    main()
