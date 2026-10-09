# CS8409 speaker audio

## What was fixed

PipeWire showed playback activity but the built-in speakers were silent. The stock
`snd-hda-codec-cs8409` loaded successfully without activating the speakers. Installing
[davidjo/snd_hda_macbookpro](https://github.com/davidjo/snd_hda_macbookpro) with DKMS
and rebooting restored audible speaker playback. No separate PipeWire configuration
change was required. Microphone, headphones and individual speaker drivers remain
untested on the recorded machine.

The tested upstream revision is:

```text
89b22ff90b86468b186706861dd18663562defa7
```

## Fresh installation

This checked recipe targets kernels 6.17 and newer; the tested kernel is 7.2.5.
Older kernels use upstream's different pre-6.17 source layout and are not supported
by this wrapper.

First confirm the problem is silent speakers, not simply muted/wrongly routed
output. Inspect `wpctl status` and select the built-in output in desktop audio
settings. Use a low desktop volume for testing.

Install the prerequisites in INSTALL.md, especially `wget`: the original first
build failed because it was missing. Prepare pinned source as your normal user:

```bash
./scripts/prepare-audio
```

This clones upstream into ignored `build/`, exports the exact commit, applies
`patches/audio-dkms-target-kernel.patch`, and adds a checked pre-build wrapper. If
you already have the upstream checkout, supply it explicitly:

```bash
./scripts/prepare-audio /path/to/snd_hda_macbookpro
```

The source is staged at `build/snd_hda_macbookpro-0.1`. Review the patch before
installation. The patch makes the DKMS build pass `KERNELRELEASE=${kernelver}`
explicitly and rejects a pre-build that reports success without producing the
expected kernel source. It does not alter codec programming or mixer settings.
These packaging changes were source-validated; a fresh host installation of this
recipe remains to be tested. The original unmodified upstream driver worked here.

Then run the fresh-install script:

```bash
sudo ./scripts/install-audio
```

It validates the model and headers, refuses an existing audio installation, copies
source into persistent `/usr/src/snd_hda_macbookpro-0.1`, and builds/installs only
this DKMS module for the selected kernel. It does not reload the current sound
module or reboot. For `linux-omarchy`, it backs up and rebuilds the UKI through
Limine and verifies the entry hash; see [BOOT-INTEGRITY.md](BOOT-INTEGRITY.md).
An explicit target kernel can be supplied as its sole argument.
Source ownership is root:root; the source does not depend on a checkout remaining
under a user's home directory.

Upstream's pre-build downloads Linux source over HTTPS from kernel.org. Future
builds therefore need network access and the upstream source layout/patches to
remain compatible. It can fall back to a base kernel source if an exact archive
is unavailable; inspect the build log and do not treat a fallback as compatibility
proof. This project does not promise offline audio rebuilds or ship kernel source.

If a build/install fails, source and registration may remain for diagnosis. Keep
them, inspect the DKMS build log, and use the targeted build/install commands in
UPGRADES.md after fixing the cause; do not rerun the fresh-install script over an
existing registration.

After a successful build, save work, reboot normally when ready, then follow the
speaker test in VERIFY.md. Confirm `modinfo -F filename snd-hda-codec-cs8409`
resolves under `updates/dkms` and its vermagic matches the booted kernel.
A successful build alone is not an audible playback test.

## Existing working installation

Do not run the installer to replace functioning audio. The historical setup has
`/usr/src/snd_hda_macbookpro-0.1` symlinked to a home-directory checkout. Keep that
checkout intact until a separately reviewed migration is complete.

A migration should back up the source/registration, export the pinned source,
move it into a persistent root-owned source directory, update only this DKMS
registration, and build for each intended kernel. Do not remove or reload a live
sound module just to relocate source. This repository deliberately does not
silently automate that migration on the already-working machine.

## Upgrades and rollback

`AUTOINSTALL=yes` and Arch DKMS hooks rebuild registered source for new kernels
with matching headers. Check the build output and run `scripts/check-upgrades`
before reboot. Failed download/patch/build steps require investigation.

To remove a failing replacement in a planned rollback:

```bash
sudo dkms remove -m snd_hda_macbookpro -v 0.1 --all
```

That operates only on this audio registration; no script here runs it automatically.
Before reboot, confirm DKMS restored the stock module and `modinfo` resolves to the
kernel module tree for the intended kernel. Preserve source and backups until
rollback is verified. Stock playback was silent on the tested machine, so removal
is a recovery step rather than a way to keep working speakers.
