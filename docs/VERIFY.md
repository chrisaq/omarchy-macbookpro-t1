# Functional verification

Run one test at a time and record only what you observed. Start with non-disruptive
tests; leave suspend and boot selection until the end. Save work before shutdown
or suspend. None of the status scripts initiates those transitions.

```bash
mkdir -p reports
./scripts/hardware-status --json > reports/before.json
```

The JSON omits hostname, serial number, machine ID, filesystem UUIDs and network
identifiers. Review it before sharing. Microphone recordings and test notes can
contain personal material; keep them local. The repository ignores `reports/`,
`results.json`, audio and video artifacts.

Record each result with the exact tested behavior:

```bash
./scripts/record-test speakers passed --notes 'Heard left then right tones through built-in speakers'
```

`hardware-status` displays detection without a functional pass until you record
one. Passes are dated user observations scoped to their kernel. A new kernel
changes the display to `previous-kernel-test`; repeat the test after upgrades.
An `untested` result explicitly resets the displayed functional conclusion without
erasing earlier history. Failed tests must be investigated before applying fixes.

## Speakers and headphones

```bash
wpctl status
```

Find the numeric node ID for the intended output. Set a low volume through the
desktop audio controls and confirm it is unmuted. Explicitly select that node:

```bash
./scripts/test-audio speakers --target <built-in-sink-node-id>
```

The script plays a quiet four-second stereo tone through PipeWire: left first,
then right. It does not write mixer settings or use direct `hw:0,0` playback.
An exit code cannot confirm that the physical speakers were audible. This test
also does not independently certify every tweeter/woofer or audio fidelity.

Connect headphones, identify the new/routed sink node and run:

```bash
./scripts/test-audio headphones --target <headphone-sink-node-id>
```

Check both channels, jack insertion/removal and restoration of speaker output.
Record headphones separately from speakers.

## Microphone

Find the built-in microphone source node in `wpctl status`. Select/unmute the
intended source in desktop settings, then:

```bash
./scripts/test-audio microphone --target <microphone-source-node-id>
pw-play --target <verified-output-node-id> reports/microphone.wav
```

Speak during the eight-second recording. The recorder writes a local file and
refuses to overwrite one. A pass requires intelligible speech from the intended
microphone, not merely nonempty data. Test headset recording separately and note
which device was used. Delete private recordings when done.

## Webcam

```bash
v4l2-ctl --list-devices
./scripts/test-webcam /dev/videoN
```

Choose the actual capture node associated with iBridge; metadata nodes may not
support video. The script opens a live preview with ffplay and saves no recording.
Move in front of it and verify clear, updating frames. Press `q` to close. Device
listing or a successful open alone is insufficient. If format negotiation fails,
inspect `v4l2-ctl --device=/dev/videoN --list-formats-ext` before choosing settings.

## Keyboard, trackpad and Touch Bar

Test normal typing in an editor, modifiers, repeating keys, trackpad click,
scrolling, configured multitouch gestures and palm rejection. Record the actual
subset you tried; ordinary pointing is not a complete gesture test.

Use `evtest` for low-level input verification if needed:

```bash
sudo evtest
```

Select the intended device; do not use `--grab`. Press Escape and each F1–F12 key
on the Touch Bar and inspect key press/release events. Input output can expose what
you type, so test only intended keys and do not publish a raw typing log.
Confirm the strip is visible as well as emitting events. Use the
[Touch Bar repository's checks](https://github.com/chrisaq/apple-t1-touchbar/blob/main/docs/INSTALL.md)
for module state, bindings and cold-boot behavior.

## Wi-Fi and Bluetooth

Use the desktop network UI to join your normal network and verify browsing or a
transfer. Test known 2.4 GHz and 5 GHz access points separately if available; note
which band was tested without publishing SSIDs/MAC addresses. Repeated connectivity
and throughput tests are separate from merely loading brcmfmac. Avoid speculative
firmware/NVRAM changes on a working link.

For Bluetooth, pair a known peripheral using desktop controls or `bluetoothctl`,
then test its actual function (typing, pointer movement, audio). Disconnect/reconnect
and record the peripheral category. Scanning alone is not a pass. Never have a
script automatically pair with unknown devices.

## Display, backlight, battery, thermals and ports

| Component | Functional test |
| --- | --- |
| Display | Inspect the image and exercise normal brightness controls |
| Keyboard backlight | Adjust it through the normal controls; visually verify changes |
| Battery | Compare charging/unplugged state and observed capacity changes over time |
| Temperatures | Compare sensible readings at idle and normal workload; no sensor accuracy claim |
| Fans | Observe normal temperature/fan behavior during ordinary use; no forced fan writes |
| USB-C | Try a known peripheral in each port; verify actual read/write or charging behavior |
| External display | Connect a monitor, verify image, resolution and hotplug/reconnect |
| Thunderbolt | Verify an actual Thunderbolt peripheral; USB-C shape alone is insufficient |

The inventory can expose readings but cannot establish their accuracy. Do not
install fan-control software or change thermal/power settings merely because a
sensor exists. ALS needs a separately planned sensor test; this guide does not
load the optional driver automatically.

## Shutdown, cold boot, suspend and macOS

For cold boot, shut down normally, wait for power-off, power on and verify the
Touch Bar, audio, Wi-Fi, display and input. Record shutdown and cold boot explicitly.

For suspend, save work, capture a baseline, use the desktop's normal suspend
control, then verify resume plus display, input, Touch Bar, audio, Wi-Fi and
Bluetooth. Inspect `journalctl -k -b` for hangs/errors and repeat several cycles
before claiming reliability. Do not add sleep hooks before observing a problem.
A single successful cycle does not establish battery drain or long-term reliability.

For macOS, shut down and use Apple's normal Option-key boot picker. Verify the
retained installation boots and Linux remains selectable. Adding a Limine entry
is separate configuration work; do not change EFI partitions during verification.

```bash
./scripts/hardware-status --json > reports/after.json
./scripts/hardware-status --results results.json
```
