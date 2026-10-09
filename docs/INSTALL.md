# Installing on a fresh machine

## Preserve the Apple firmware first

Confirm the model is MacBookPro13,2. Back up personal data and the original Apple
EFI partition before changing the disk. Verify that backup independently. This
project does not supply destructive partitioning commands or distribute firmware.

The T1 depends on firmware preserved on Apple's original EFI partition, including
`EFI/APPLE/EMBEDDEDOS/combined.memboot`. Erasing that partition can leave the T1 in
recovery mode and affect the Touch Bar, webcam and related functions.

The tested installation retained the original Apple EFI partition and a macOS
APFS container, then installed Omarchy into remaining free space. The original
APFS filesystem was corrupted, so macOS was reinstalled from Internet Recovery
after backing up data. That repair was specific to this machine; do not delete a
healthy APFS container merely to imitate it. Approximate sizes are historical
examples, not requirements. See INSTALLATION-RECORD.md.

Use the Omarchy installer appropriate to the release you are installing and its
free-space installation option. Review the proposed partition changes before
applying them. Installer screens and available options can change; this guide
records the successful layout rather than prescribing unverified clicks for
future releases. Boot the installed Linux system before installing extra drivers.

## Establish the baseline

```bash
cat /sys/class/dmi/id/product_name
uname -r
lsusb -d 05ac:8600
./scripts/hardware-status
```

The expected model is MacBookPro13,2 and T1 USB ID is `05ac:8600`. If it is absent
or shows `05ac:1281`, stop and investigate firmware preservation; a Touch Bar
module installation cannot repair missing Apple firmware.

Display and keyboard should already be usable. On the tested installation, Wi-Fi
initially connected without firmware extraction or NVRAM edits, but subsequent
weak-reception testing found missing board configuration. A model-specific NVRAM
candidate restored 5 GHz and improved reported link metrics; see [WIFI.md](WIFI.md)
for the public prepare/install/rollback scripts and persistent upgrade checks. Use normal
Omarchy network setup and test actual connectivity before considering driver fixes.
The kernel's `applespi` supplied keyboard/trackpad support; do not install a second
SPI driver merely because a guide mentions one.

## Dependencies

For Omarchy's kernel, install its matching headers. On another Arch kernel use
that kernel's own headers package instead:

```bash
sudo pacman -S --needed base-devel git dkms linux-omarchy-headers wget patch usbutils python iw binutils
```

This command installs prerequisites; it does not initiate a kernel upgrade.
Follow the distribution's full-system upgrade policy if package versions are out
of sync. Confirm `/usr/lib/modules/$(uname -r)/build/include` exists before a driver
build. If the running kernel no longer has installed headers, resolve that mismatch
using the normal boot/upgrade workflow first.

Optional test tools:

```bash
sudo pacman -S --needed v4l-utils ffmpeg evtest
```

PipeWire's `wpctl`, `pw-play` and `pw-record` are used for audio tests. Bluetooth
pairing tests use `bluetoothctl`. Missing tools are reported without automatically
installing packages.

## Fix only demonstrated problems

For silent built-in speakers, follow AUDIO.md. Its fresh-install script refuses
to replace an existing audio driver, including this machine's working setup.

For the Touch Bar, use
[chrisaq/apple-t1-touchbar](https://github.com/chrisaq/apple-t1-touchbar), beginning
with its [installation guide](https://github.com/chrisaq/apple-t1-touchbar/blob/main/docs/INSTALL.md).
That project contains the complete driver and upgrade-managed package. Follow its
manual activation and cold-boot checkpoints before enabling automatic activation.
The URL is the intended public repository; it was not publicly retrievable during
preparation of this guide. Until published, use the local sibling checkout.

## Validate before further customization

Use VERIFY.md and record what actually works. Verify clean shutdown and cold boot
before attempting suspend. Webcam detection is not a video test, and a PipeWire
source is not a microphone test. Preserve the working audio, Wi-Fi and keyboard
configuration while testing remaining devices.

The historical Limine hash mismatch was repaired and verified, and the user
confirmed the warning was gone after reboot; see [BOOT-INTEGRITY.md](BOOT-INTEGRITY.md). macOS boot selection remains
a separate check.
Use the Apple boot picker to verify macOS independently; do not assume that a
missing Limine entry means macOS was erased. Do not disable hash verification or
edit Apple partitions to hide a boot warning. See UPGRADES.md.
