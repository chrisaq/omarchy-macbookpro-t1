# Hardware compatibility

Snapshot: MacBookPro13,2, Omarchy 4.0.4 / Quattro, kernel 7.2.5-3-omarchy,
2026-10-09. “Working” reflects reported functional tests, not just driver loading.

| Component | Status | Evidence / remaining test |
| --- | --- | --- |
| Built-in display | Working | Desktop usable |
| Intel graphics | Seemingly working | Hyprland on i915; acceleration/load not separately tested |
| Wi-Fi BCM43602 | Working | Initial connectivity worked; NVRAM test restored 5 GHz and improved reported link metrics; throughput untested; failed suspend abort leaves Wi-Fi unusable |
| Keyboard | Working | Normal typing |
| Trackpad | Seemingly working | Normal desktop use; gestures/palm rejection untested |
| Touch Bar Escape/F1–F12 | Working | Manual activation, service, clean shutdown and cold boot passed |
| Touch Bar graphical modes | Untested | Keyboard mode is the supported route |
| Built-in speakers | Working | Audible playback after patched CS8409 driver and reboot |
| Microphone / headphone jack | Untested | Real recording/playback needed |
| Webcam | Detected | uvcvideo/PipeWire devices; image capture not yet verified |
| Bluetooth | Detected | Controller present; pairing/playback untested |
| Keyboard backlight | Detected | Sysfs device; adjustment untested |
| Battery | Detected | Capacity/status readable; health and discharge accuracy untested |
| Temperatures | Detected | hwmon readings available; sensor accuracy/load behavior untested |
| Fans | Untested | No control or load test; do not install speculative fan software |
| Ambient light sensor | Untested | Optional driver available, not activated by Touch Bar service |
| Suspend / resume | Failing | Wi-Fi D3 handshake aborts suspend; Touch Bar also remains off; see [SUSPEND.md](SUSPEND.md) |
| USB-C | Seemingly working | USB installer booted; port/data/charging combinations untested |
| External displays / Thunderbolt | Untested | Real peripheral tests required |
| Touch ID | No supported setup established | This guide provides no fingerprint driver |
| macOS boot selection | Needs verification | Retained macOS; Limine entry absent in historical record |
| Limine image hash | Fixed | Scripted UKI rebuild synchronized the hash; user confirmed warning gone after reboot |

The `macbook12-spi-driver/0+git.315` registration is only `added`; it is not evidence
of an installed DKMS SPI driver. The loaded kernel applespi supplied input support.

The status collector intentionally does not import these historical passes into a
new machine's results. Test your own hardware and record dated observations.
