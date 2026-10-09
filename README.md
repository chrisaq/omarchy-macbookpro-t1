# MacBookPro13,2 · Omarchy

**A reproducible setup guide for the 2016 13-inch MacBook Pro with Apple T1.**

Installation notes, the working audio recipe, hardware checks and recovery paths
for Omarchy on this model. The goal is a usable machine and an honest compatibility
record: a detected device is not automatically a working device.

| Tested baseline | Value |
| --- | --- |
| Hardware | MacBookPro13,2 · Intel Core i5 · 16 GB RAM |
| OS | Omarchy 4.0.4 / Quattro |
| Kernel / headers | `7.2.5-3-omarchy` / `linux-omarchy-headers 7.2.5-3` |
| DKMS | 3.4.3 |
| Boot | Limine UKI · encrypted Btrfs root |
| Validation date | 2026-10-09 |

Display, normal keyboard use, Wi-Fi connectivity and built-in speaker playback
were tested. Escape/F-keys, automatic Touch Bar activation, clean shutdown and
cold boot were also confirmed. Other functionality is listed individually in
[the compatibility matrix](docs/HARDWARE.md); this is not an “everything works” claim.

## Setup route

1. [Preserve firmware and install Omarchy](docs/INSTALL.md).
2. [Install the pinned CS8409 audio driver](docs/AUDIO.md) if speakers are silent.
3. Install [chrisaq/apple-t1-touchbar](https://github.com/chrisaq/apple-t1-touchbar)
   for the Touch Bar. Its driver, package, service and recovery guide live there.
4. Use the [scripted Wi-Fi setup](docs/WIFI.md) if reception is unexpectedly weak.
   It pins the tested candidate and asks for this machine's original Wi-Fi MAC.
5. [Test hardware and record observations](docs/VERIFY.md).
6. [Check upgrades and recovery](docs/UPGRADES.md).

No all-in-one script repartitions disks, installs drivers or reboots. Read-only
checks and active tests are separate, and installation commands must be invoked
explicitly. The scripts do not replace working Wi-Fi/input drivers or change
power-management settings.

## Check this machine

```bash
./scripts/hardware-status
mkdir -p reports
./scripts/hardware-status --json > reports/status.json
sudo ./scripts/check-upgrades
```

The inventory reads module state, USB/HID bindings, battery/sensor data and DKMS
metadata. It does not change configuration, play sound, access the camera, collect
network identifiers or elevate privileges. Restricted/missing tools are reported
as unavailable, not as working hardware.

Record an actual test after following the checklist:

```bash
./scripts/record-test touchbar passed --notes 'Escape and F1-F12 respond after cold boot'
./scripts/hardware-status --results results.json
```

Results remain local and are ignored by Git. Each observation carries a kernel
version and date; tests from an older kernel are marked as previous-kernel tests.
A recorded pass is a user observation, not independent automated certification.

## What is included

| Path | Contents |
| --- | --- |
| `docs/` | Installation, audio, compatibility, functional tests and recovery |
| `scripts/hardware-status`, `record-test` | Inventory and dated test records |
| `scripts/test-audio`, `test-webcam` | Explicit playback, recording and live-video tests |
| `scripts/prepare-audio`, `install-audio` | Pinned upstream audio source and fresh installation |
| `scripts/wifi`, `packaging/` | Pinned Wi-Fi candidate preparation, install/adopt, rollback and upgrade validation |
| `scripts/boot-integrity` | UKI hash checking and backed-up Limine rebuild |
| `patches/` | Small audio DKMS target-kernel/pre-build patch |
| `tests/` | Result classification and audio pre-build failure checks |

See [the installation record](docs/INSTALLATION-RECORD.md) for the actual historical
procedure and [validation](docs/VALIDATION.md) for what was checked while preparing
this repository. GPL-2.0-only; upstream driver credit is retained. Audio source is
fetched from its pinned upstream revision, and no Apple firmware is distributed.

Boot checksum warnings and scripted repair: [BOOT-INTEGRITY.md](docs/BOOT-INTEGRITY.md).
