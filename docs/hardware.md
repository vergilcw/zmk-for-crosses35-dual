# Hardware & firmware architecture

## Halves

| | Right (`crosses_right`) | Left (`crosses_left`) |
| --- | --- | --- |
| Split role | **Central** (talks to host, USB + BLE) | Peripheral (talks only to right half) |
| ZMK Studio | Yes (`studio-rpc-usb-uart` snippet, `CONFIG_ZMK_STUDIO=y`) | No |
| Trackball | PMW3610, CPI 800, `force-high-performance` → rotated 45° CCW; **pointer** (Base/Mouse), **scroll** (Lower), **snipe** (Raise) | PMW3610, CPI 600 → **scroll** (`zip_xy_to_scroll_mapper` + `zip_scroll_scaler 1 2`) |
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

- `crosses.conf`: `ZMK_SLEEP=y` (15 min idle), battery reporting, pointing + smooth scrolling, USB,
  `ZMK_STUDIO_LOCKING=n` (but the device *does* report LOCKED until `&studio_unlock` — see KB),
  `ZMK_BLE_MOUSE_REPORT_QUEUE_SIZE=1`, `ZMK_BLE_EXPERIMENTAL_FEATURES=y`, `BT_CTLR_TX_PWR_PLUS_8`,
  `BT_CTLR_TX_PWR_DYNAMIC_CONTROL`, `BT_CTLR_PHY_2M`, `BT_PERIPHERAL_PREF_MAX_INT=6`, `BT_TPS`,
  `BT_GATT_ENFORCE_SUBSCRIPTION=n`, PMW3610 rest/downshift timings, report-rate limit default 2 ms.
- Halves' `.conf`s repeat most BLE settings and set `PMW3610_INIT_POWER_UP_EXTRA_DELAY_MS=1500`,
  anti-warp.
- `crosses_right.overlay` uses `xy-swap` with `x-invert`/`y-invert` commented out; that's where
  orientation is currently set.

## Right-trackball event chain (keymap file)

```
trackball_central (driver) → trackball_central_listener [shield; input-processors = zip_rotate_pointer]
  → zip_rotate_pointer (efogdev/zmk-input-processor-rotate-plane, angle 45)
  → rotated_pointer_listener [config/crosses.keymap]
       base:  zip_ble_report_rate_limit
       LOWER: zip_xy_to_scroll_mapper → zip_scroll_scaler 1 2 → rate limit
       RAISE: zip_xy_scaler 1 4 → rate limit
```

The left ball is untouched (always scroll). Details and sign conventions: knowledge base, "Right trackball port".

## Physical layout

`config/info.json` (QMK format, `gggw_crosses_36_layout`) drives keymap-drawer only. Key index order
is row-major: 10 + 10 + 10 + 6 thumbs; positions 0–4/10–14/20–24/30–32 are the left half.
