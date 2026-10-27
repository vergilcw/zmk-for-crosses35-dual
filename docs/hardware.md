# Hardware & firmware architecture

## Halves

| | Right (`crosses_right`) | Left (`crosses_left`) |
| --- | --- | --- |
| Split role | **Central** (talks to host, USB + BLE) | Peripheral (talks only to right half) |
| ZMK Studio | Yes (`studio-rpc-usb-uart` snippet, `CONFIG_ZMK_STUDIO=y`) | No |
| Trackball | PMW3610, CPI 800, `force-high-performance` → rotated 45° CCW; **pointer** (Base/Mouse), see "Trackball behaviour by layer" | PMW3610, CPI 600 → **scroll**, vertical only (horizontal-only while Lower/Raise held), rotated 45° CW; (`zip_xy_to_scroll_mapper` + `zip_scroll_scaler 1 32`) |
| USB name | `Crosses BT` (`/dev/serial/by-id/usb-ZMK_Project_Crosses_BT_*`) | — |
| Artifact | `crosses_35_right` | `crosses_35_left` |

Controller: nice!nano (nRF52840), board `nice_nano` in `build.yaml`. 128x32
SSD1306 OLED per half on I²C (P1.04/P1.06). Trackballs on SPI1 (SCK P0.17,
SDIO P0.20, CS P1.00, IRQ P0.06). Matrix is `row2col`, 5 row GPIOs × 6 cols
per half, of which the 36-key transform is used.

## Where things are defined

ZMK user config builds layer config from several places (later wins):

1. **ZMK** — pinned commit `ac7f75b8…` on `main` (`config/west.yml`).
2. **`HeeTuic/cb-zmk-keebs@zephyr-4.1`** (imported via west; floating branch!) provides
   `boards/shields/crosses/`: `crosses.dtsi` (matrix, physical layouts 54/42/36, input listeners,
   split input node, `rrl` polling-rate behavior), `crosses_{left,right}.overlay` (pins, trackball
   nodes, OLED), `crosses*.conf` (BLE tuning, PMW3610 tuning, sleep), `Kconfig.defconfig` (name,
   central role). Its own `config/west.yml` pulls:
   - `efogdev/zmk-pmw3610-driver@zephyr-4.1` (compatible `pixart,pmw3610-efogtech`)
   - `efogdev/zmk-report-rate-limit@main` (`zip_ble_report_rate_limit`)
   - `badjeff/zmk-input-processor-xyz@main`
   - `caksoylar/zmk-rgbled-widget@e9472d6`
3. **This repo** — `config/crosses.conf`, `config/crosses.keymap` (chooses the 36-key physical layout).
4. **ZMK Studio settings** stored in the right half's flash — override keymap bindings at runtime
   (see keymap-workflow.md).

Snapshot of the inherited shield settings (2026-10-10, `cb-zmk-keebs` HEAD `d9e64a4`):

- `crosses.conf`: `ZMK_SLEEP=y` (15 min idle), battery reporting, pointing + smooth scrolling (overridden off in our `config/crosses.conf`, see KB), USB,
  `ZMK_STUDIO_LOCKING=n` (but the device *does* report LOCKED until `&studio_unlock` — see KB),
  `ZMK_BLE_MOUSE_REPORT_QUEUE_SIZE=1`, `ZMK_BLE_EXPERIMENTAL_FEATURES=y`, `BT_CTLR_TX_PWR_PLUS_8`,
  `BT_CTLR_TX_PWR_DYNAMIC_CONTROL`, `BT_CTLR_PHY_2M`, `BT_PERIPHERAL_PREF_MAX_INT=6`, `BT_TPS`,
  `BT_GATT_ENFORCE_SUBSCRIPTION=n`, PMW3610 rest/downshift timings, report-rate limit default 2 ms.
- Halves' `.conf`s repeat most BLE settings and set `PMW3610_INIT_POWER_UP_EXTRA_DELAY_MS=1500`,
  anti-warp.
- `crosses_right.overlay` uses `xy-swap` with `x-invert`/`y-invert` commented out; that's where
  orientation is currently set.

## Trackball behaviour by layer (config/crosses.keymap)

| Layer | Right ball (central) | Left ball (via split) |
| --- | --- | --- |
| Base | pointer, rotated 45° CCW | vertical-only scroll, unrotated |
| Lower (hold `Del`, `V` or `M`) | vertical-only scroll, unrotated | vertical-only scroll, unrotated |
| Raise | snipe (¼ speed), rotated 45° CCW | horizontal-only scroll, rotated 45° CW |
| Mouse (hold `Tab`) / RMouse (hold `,`) | pointer, rotated 45° CCW | vertical-only scroll, unrotated |
| LMouse (hold `C`) | pointer, rotated 45° CCW | pointer, rotated 45° CW (module angle 135, see KB) |

LMouse (left-handed mouse): left thumbs are M3/M2/M1 = Tab-pos / Shift-pos / Del-pos; the right half has the Mouse-layer
nav cluster (Home ↑ End / ← ↓ → in the same left-to-right order, not mirrored, index finger = ←/Home) with clicks on the
bottom row (index = LCLK, then RCLK, MCLK). On LMouse the `V` position and on RMouse the `M` position are `&mo LOWER`, so hold `C` then `V` (or `,` then `M`) scrolls both
balls while the pointer-layer keys keep working (Lower is a lower layer index, so LMouse/RMouse `&none`/clicks still win; the
listeners list the Lower child first). RMouse: right thumbs are LCLK/RCLK/MCLK and the left half has the Mouse layer's
cluster and clicks (index = LCLK, then RCLK, MCLK to the left) without its Bluetooth keys. Everything else is `&none`. The goal is one scheme that can be copied to the
single-trackball unibody boards.

Rotation is a separate input-processor *device* (efogdev rotate-plane), so each ball is two stages:

```
right: trackball_central → trackball_central_listener [shield node; processors = zip_rotate_pointer]
          children LMOUSE/RMOUSE: rotate (explicit, listed first)
          child LOWER: x_scaler 0 → mapper → scroll_transform Y_INVERT → scroll_scaler 1 32 → rate limit  (final)
       → zip_rotate_pointer (angle 45) → rotated_pointer_listener
          base: rate limit      child RAISE: xy_scaler 1 4 → rate limit

left:  left half: trackball_peripheral → trackball_peripheral_split [processors = rate limit only, raw X/Y]
       central:   trackball_peripheral_listener [processors = x_scaler 0 → mapper → scroll_scaler 1 32]
          children LMOUSE, RAISE: processors = zip_rotate_left (angle 135)
       → zip_rotate_left → left_ball_listener
          base: (none = pointer)   child RAISE: y_scaler 0 → mapper → scroll_scaler 1 32
```

A matching `layers` child *replaces* the listener's base chain, which is how Lower skips rotation. Layer state
only exists on the central, so the left half does no layer-dependent work. Sign conventions: knowledge base.

## Physical layout

`config/info.json` (QMK format, `gggw_crosses_36_layout`) drives keymap-drawer only. Key index order
is row-major: 10 + 10 + 10 + 6 thumbs; positions 0–4/10–14/20–24/30–32 are the left half.
