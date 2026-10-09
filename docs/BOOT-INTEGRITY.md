# Limine BLAKE2b boot-image verification

## Cause and confirmed result

Limine's Linux entry records a BLAKE2b-512 digest after the UKI path:
`boot():/EFI/Linux/omarchy_linux-omarchy.efi#<128 hexadecimal characters>`.
The UKI contains the kernel, initramfs and other boot data. If its bytes change
without updating this entry, Limine reports a checksum mismatch and, on the
recorded setup, asks whether to continue. SHA-512 is a different algorithm.
This is separate from Secure Boot signatures and Limine configuration enrollment.

On 2026-10-09 the checker confirmed that the recorded machine's UKI and entry
had different BLAKE2b hashes. A rebuild using the installed Limine integration
updated both, and the post-check verified matching hashes and the embedded
`7.2.5-3-omarchy` kernel release. The user subsequently rebooted and confirmed that the
warning disappeared. The exact earlier operation that left the stale entry
has not been established; do not attribute it to every DKMS installation.
The recent manual Touch Bar and Wi-Fi installers explicitly checked that their
operations left the UKI unchanged.

Direct `mkinitcpio` UKI regeneration, in-place image editing or restoring only
one of the UKI/configuration pair can cause this mismatch if the corresponding
Limine entry is not synchronized. Manual DKMS installs change module files and
can require an initramfs rebuild, but do not themselves guarantee one. Old
`REMAKE_INITRD` settings are deprecated in the installed DKMS version.

For diagnostic extraction, always supply an output image to `objcopy`, even when
using `--dump-section`; an input-only invocation permits it to rewrite the input.
For example, use temporary output files rather than editing the live UKI:

```bash
work=$(mktemp -d)
sudo objcopy --dump-section ".initrd=$work/initrd" \
  /boot/EFI/Linux/omarchy_linux-omarchy.efi "$work/copy.efi"
sudo lsinitcpio "$work/initrd"
sudo rm -r -- "$work"
```

## Check and repair

From this checkout:

```bash
sudo ./scripts/boot-integrity
sudo ./scripts/boot-integrity --repair
```

The first command is read-only and returns failure for a missing, malformed or
mismatched hash. It checks every reference to this specific UKI in
`/boot/limine.conf`; it does not claim to verify snapshots, another ESP, other
kernels or Apple boot files. Unsupported layouts stop for investigation.

Repair requires MacBookPro13,2, a separately mounted `/boot`, the installed
`linux-omarchy` package and the installed Limine integration. It saves the UKI
and configuration in a private timestamped directory under
`/var/lib/macbookpro13-2-omarchy/boot-backups`, then runs:

```bash
sudo limine-mkinitcpio linux-omarchy
```

This is the host's supported targeted workflow: it builds a temporary UKI,
installs it and updates its entry via `limine-entry-tool`, including the host's
normal boot hooks. The helper saves the build log, rejects reported errors,
checks the resulting image's embedded kernel release and recomputes its hash.
It does not reboot, reload running drivers, reset the Limine menu, deploy the
bootloader binary or change Apple partitions. Existing host boot hooks still run.
Do not use `omarchy refresh limine` as a routine checksum repair: it resets
configuration. Do not manually paste a new digest into the menu or disable
verification to conceal an unexplained image change.

If repair fails, preserve its backup/log and inspect the failure before reboot.
The helper does not automatically roll back a partially completed host workflow.
Backups contain boot configuration and should remain private; do not commit them.
When ready, boot the normal Linux entry and confirm the warning is gone, then
check Touch Bar, Wi-Fi, audible audio and clean shutdown again.

## Upgrade automation

On the recorded host, the effective `90-mkinitcpio-install.hook` runs
`/usr/share/libalpm/scripts/limine-mkinitcpio-install` after the `70-dkms` hooks.
Its triggers include kernel, firmware, initcpio and DKMS source changes. Normal
package transactions therefore rebuild boot images and synchronize entries.
Watch transaction output: a successful package installation alone does not prove
that a boot-image build succeeded.

The fresh audio installer now invokes the verified rebuild after a manual DKMS
install targeting `linux-omarchy`. `scripts/check-upgrades` checks boot integrity
alongside driver builds; run it with sudo so it can read `/boot`. After a manual
audio repair, invoke `scripts/boot-integrity --repair` too. The Touch Bar package
provides its own identical helper and runs the check in its post-transaction
validation; its manual repair command rebuilds and verifies the Omarchy UKI.
Other kernel layouts require their distribution's boot-image workflow.

The runtime-only Wi-Fi calibration installer and service activation leave the UKI
unchanged and do not need to rebuild it. If Wi-Fi firmware is later embedded in
an initramfs, rebuild with the supported workflow after changing that firmware.
No background or boot-time task silently replaces hashes.

References: [Limine verification syntax](https://github.com/limine-bootloader/limine/blob/v12.x/USAGE.md)
and [limine-entry-tool workflow](https://gitlab.com/Zesko/limine-entry-tool/-/blob/master/README.md).
The hook order and targeted command above were also checked against the installed
scripts on this Omarchy host.
