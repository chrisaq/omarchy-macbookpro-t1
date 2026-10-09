# Installation record · 2026-10-09

This is a historical snapshot of the actual MacBookPro13,2 setup. It preserves
what was done without presenting machine-specific recovery steps as prerequisites
for every installation. Functional status is summarized in HARDWARE.md.

## Disk and operating system

The machine is a 2016 13-inch MacBook Pro with a 2.9 GHz dual-core Intel Core i5,
16 GB RAM and T1. Its prior OS was macOS Monterey. The original APFS filesystem
had unrepaired orphaned records. After personal-data backup, Internet Recovery
was used to recreate the damaged APFS container and reinstall macOS.

The original Apple EFI partition was preserved. The resulting layout had an
approximately 314.6 MB original Apple EFI partition, a 90 GB macOS APFS container
and approximately 160 GB for the Linux EFI/encrypted-root installation. Omarchy
was installed using the free-space option. The EFI firmware backup's location and
verification were not recorded; this guide does not claim that backup is verified.
MacOS boot selection was not subsequently confirmed.

The current read-only snapshot reports Omarchy 4.0.4, kernel 7.2.5-3-omarchy,
matching linux-omarchy headers and DKMS 3.4.3. Limine boots a UKI; the Linux root
uses encrypted Btrfs. No UUIDs, serials or hostname are included in this public record.

## Wi-Fi and input

Broadcom BCM43602 (PCI 14e4:43ba, Apple subsystem 106b:0157) connected without
manual firmware/calibration/NVRAM changes. A prior brcmfmac ARP-table error was
observed alongside functioning connectivity; it was not treated as proof of failure.
Bands, throughput and resume were not independently verified.

The kernel's applespi supplied working typing and observed trackpad use. An
additional macbook12-spi-driver registration was only `added`, not built/installed.
No second SPI driver was installed. applesmc and apple_mfi_fastcharge were detected;
fan control, thermal accuracy and charging behavior were not functionally tested.

## Audio

PipeWire 1.6.8 showed an internal playback/capture device but speakers were silent.
The codec was Cirrus CS8409; Intel Skylake HDMI was also detected.

Upstream davidjo/snd_hda_macbookpro at commit
`89b22ff90b86468b186706861dd18663562defa7` was used. Its checkout was registered via
a `/usr/src/snd_hda_macbookpro-0.1` symlink, then `dkms add/build/install` for the
running kernel. The initial pre-build failed because wget was absent. Installing
wget allowed the build to succeed. DKMS installed the replacement under
`updates/dkms`; vermagic matched the kernel, and speakers were audible after reboot.
No PipeWire configuration changes were necessary. The working audio source was not
modified during Touch Bar troubleshooting or this documentation task.

The new AUDIO.md recipe stages that exact revision and adds a small build-only
patch. That revised installation has not replaced the historical working driver.

## Touch Bar

The normal-mode T1 appeared as 05ac:8600. Initial manual activation showed Escape
and F1–F12, but later auto-mode alias loading deadlocked during USB configuration
switching inside a HID probe. The journal traced the blocked task through
usb_set_configuration, hid_destroy_device and device_del.

The coordinator was patched to use USB core's deferred configuration helper.
All three modules built successfully. Explicit keyboard mode retained configuration
1; the coordinator reached live. The second HID interface was handed over from
hid-sensor-hub before loading the Touch Bar subdriver. Both interfaces used
apple-ibridge-hid and controls were fnmode=0, idle_timeout=-1, dim_timeout=-1.

Manual input, activation-service idempotence, clean shutdown, cold boot and
Escape/F-key use after login were confirmed. The service was enabled for late
activation and module blacklists retained. Source is still installed manually as
appleibridge/0.1; the standalone public package was prepared and built but not
migrated onto this machine during repository preparation.

See [apple-t1-touchbar](https://github.com/chrisaq/apple-t1-touchbar) for code and
operational instructions. Graphical modes and suspend/resume remain untested.

## Remaining work

The webcam is detected but usable video was not verified. Microphone, headphones,
Bluetooth pairing, keyboard backlight adjustment, detailed trackpad gestures,
battery accuracy, thermal/fan behavior, ALS, external monitors, Thunderbolt and
suspend/resume still need real tests. Basic battery and temperature values are
readable; that is detection evidence only.

The historical Limine image-hash warning was subsequently repaired; see the
boot integrity follow-up below. Verification remains enabled.
The next checks should follow VERIFY.md one at a time.

## Subsequent Wi-Fi calibration test

After the initial setup record, weak reception prompted a read-only investigation
and a controlled model-specific NVRAM test. Wi-Fi remained working after cold boot;
Band 2 appeared and the connection moved to 5200 MHz, reporting -49 dBm and RX
360 / TX 121.5 Mbit/s. Before testing, only Band 1 appeared and the last baseline
was -94 dBm at 2437 MHz with RX/TX 1 Mbit/s. Power saving and regulatory settings
were unchanged. See WIFI.md for provenance, measurement limitations and remaining
throughput/stability tests. The initial out-of-box connectivity statement remains
a historical fact; it did not establish adequate reception or full band support.

## Boot integrity follow-up (2026-10-09)

The read-only BLAKE2b checker confirmed the current UKI differed from Limine's
recorded hash. The backed-up repair ran `limine-mkinitcpio linux-omarchy`, rebuilt
the `7.2.5-3-omarchy` UKI and updated `/boot/limine.conf`. The resulting BLAKE2b
hash matched every reference to this image, and its embedded kernel release
matched the installed package. The user subsequently rebooted and confirmed
that the warning was gone. The exact historical operation causing the stale
digest has not been established.

## Public Wi-Fi maintenance follow-up

The successful private experiment now has a public, pinned preparation/install/
adopt/check/rollback workflow and persistent upgrade validation in this repository.
The personalized calibration file is not published. The user successfully adopted the existing working candidate through the public
script. It installed persistent validation helpers and the pacman hook without
rewriting the NVRAM file, reloading Wi-Fi or rebuilding the UKI. The boot hash
remained valid and no early Wi-Fi files were present.
