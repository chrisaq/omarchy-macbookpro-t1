# Upgrades, boot verification and recovery

Use Omarchy's normal full-system update process. Keep each installed kernel's
matching headers. Arch DKMS hooks rebuild registered audio/Touch Bar/Wi-Fi resume source when
kernels and source packages change; `AUTOINSTALL=yes` alone does not guarantee a
future source patch will compile or hardware will function.

Before rebooting after an upgrade:

```bash
sudo ./scripts/check-upgrades
```

This checks every installed kernel module tree, including a newly installed kernel
that differs from `uname -r`. It requires matching headers, both DKMS registrations
and appropriate module paths/vermagic, plus primary UKI integrity and the registered
Wi-Fi candidate/early-boot data. The packaged Touch Bar's own integrity check
runs too when available. No rebuild, reload, service restart or reboot occurs.

If an audio build failed, inspect its DKMS make.log and source-download/patch
errors. Rebuild only the intended driver for the intended kernel after fixing the
cause:

```bash
sudo dkms build -m snd_hda_macbookpro -v 0.1 -k <kernel-release> --force
sudo dkms install -m snd_hda_macbookpro -v 0.1 -k <kernel-release> --force
sudo ./scripts/boot-integrity --repair
```

Do not run broad force-rebuild/remove commands against unrelated working drivers.
Audio source must remain at its registered location. The historical home-directory
symlink is still in use on the recorded machine; the fresh-install recipe copies
source to persistent root-owned `/usr/src` instead.

The Touch Bar's
[upgrade/recovery guide](https://github.com/chrisaq/apple-t1-touchbar/blob/main/docs/UPGRADES.md)
covers its package, repair command and early-boot protections. Keep its blacklist
and deliberate late activation. If its checks fail, disable activation before a
planned recovery boot rather than repeatedly reloading a stuck module.

After booting the upgraded kernel, repeat the functional checks in VERIFY.md and
record new observations. Build metadata cannot prove audible playback, usable
camera frames or successful suspend/resume.

## Limine / UKI warning

See [BOOT-INTEGRITY.md](BOOT-INTEGRITY.md) for the confirmed BLAKE2b mismatch,
its verified repair, backups and upgrade integration. Before reboot, check:

```bash
sudo ./scripts/boot-integrity
```

If a known boot-image change left the entry stale, rebuild and verify with:

```bash
sudo ./scripts/boot-integrity --repair
```

## Wi-Fi maintenance

The [Wi-Fi resume DKMS guide](WIFI-RESUME.md) covers package installation,
migration, failed rebuilds and stock rollback. Its package hook runs after DKMS
and UKI hooks. Run `sudo mbp13-2-wifi-resume-check --all` before rebooting after
upgrades; `check-upgrades` also invokes it when installed. A failed pacman hook
does not undo the transaction.

See [WIFI.md](WIFI.md) for the persistent pacman check hook, adoption of an existing
working candidate, scripted rollback and `wifi sync-boot` when early firmware
needs refreshing. The hook validates rather than silently replacing files.

## Recovery

Preserve backups and a known-good boot option through the distribution's normal
process. For a Touch Bar hang, keep the service disabled and all three module
blacklists intact. Never force-unload a module in `coming`. An uninterruptible
kernel deadlock may require forced power-off.

For audio rollback, follow AUDIO.md and verify the original stock module is
restored before a later boot. Removal may bring back silent speakers. Do not
remove a working audio driver just to test another component.

For firmware/partition damage, use your verified original backup and an appropriate
Apple recovery procedure. This guide contains no disk-wiping or firmware-restoration
script. MacOS boot selection and firmware backup verification remain separate tasks;
the historical Limine mismatch was repaired and the user confirmed the warning
was gone after reboot.

Wi-Fi suspend firmware reprobe now has a [DKMS package, migration and rollback guide](WIFI-RESUME.md). Kernel upgrades require matching headers and successful checks before reboot.
