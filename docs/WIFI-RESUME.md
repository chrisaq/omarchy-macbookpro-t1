# Wi-Fi after suspend: tested patch and DKMS installation

This is separate from the [Wi-Fi calibration file](WIFI.md). The stock BCM43602
resume path sometimes reused firmware which subsequently stopped responding to
commands. On this MacBookPro13,2, forcing the driver's existing firmware reprobe
path restored connectivity through repeated normal and lid suspend cycles.
The exact cause of the firmware failure remains unconfirmed. The patch is
restricted to Apple MacBookPro13,2 and PCI 14e4:43ba / 106b:0157, BCM43602.

The tested kernel is **7.2.5-3-omarchy**. Lid opening still requires a brief power
button press to wake this machine. This package does not fix lid wake, replace
firmware or calibration, or replace the [Thunderbolt suspend guard](SUSPEND.md).
Long sleep, battery drain and future kernel compatibility remain unverified.

## Build and install, including migration from the experiment

Install `dkms`, `gcc`, `make`, `binutils`, `python`, `patch` and matching headers
for every installed kernel. Keep this checkout and rollback instructions locally.
Run from the repository root as your ordinary user:

```bash
scripts/build-wifi-resume-package
```

The builder verifies the pinned Linux 7.2.5 archive, applies the reviewed patch
without fuzz, and creates a source-only package in `build/wifi-resume-package/`.
It never installs a package or reloads a driver. Review the generated PKGBUILD,
source provenance and `packaging/wifi-resume/` before installation.

```bash
sudo scripts/install-wifi-resume-package \
  build/wifi-resume-package/mbp13-2-brcmfmac-dkms-7.2.5.1-1-x86_64.pkg.tar.zst
```

The installer checks the model, PCI identity, package checksum, kernel headers,
UKI integrity and absence of early-boot Wi-Fi. It backs up and removes the old
kernel-specific experiment override, then installs the DKMS package and verifies
all installed kernels. Stock modules remain installed. If migration fails, the
old override is restored when applicable; the package transaction can still have
completed. Preserve the printed backup and resolve the failure before rebooting.

After successful installation, reboot when convenient and run:

```bash
sudo mbp13-2-wifi-resume-check --all
sudo scripts/suspend-test normal
```

Confirm actual connectivity, Touch Bar and touchpad after wake. Test ordinary
suspend and lid closure too; passing a build check does not prove resume works.

## Kernel and package upgrades

DKMS builds the bundled patched source for new kernels when matching headers are
installed. A post-transaction hook checks source files, DKMS installation,
selected module, kernel version and UKI hashes. It also reports whether the
running module matches the built source. Only `brcmfmac` is installed; vendor
helper modules remain supplied by the kernel package.

```bash
sudo mbp13-2-wifi-resume-check --all
sudo scripts/check-upgrades
```

**Do not boot an upgraded kernel after a failed check.** Pacman hook failure does
not undo an upgrade. Read the DKMS make log under
`/var/lib/dkms/mbp13-2-brcmfmac/7.2.5.1/<kernel>/x86_64/log/`, install missing
headers, and retry `sudo dkms autoinstall -k <kernel>` before checking again.
If a later kernel changes the driver API, this pinned source needs a reviewed
update or rollback; DKMS cannot guarantee compatibility with future releases.
No download or patch regeneration runs automatically during upgrades.

The source package version is 7.2.5.1, meaning Linux 7.2.5 source plus this patch.
Update source pin, checksum, patch, package/DKMS versions and checker together
when maintaining the recipe. Rebuild and test before distributing that update.
See [upgrade guidance](UPGRADES.md) for the other hardware packages.

## Restore the stock driver

```bash
sudo scripts/remove-wifi-resume-package
```

This removes only `mbp13-2-brcmfmac-dkms`, runs depmod, verifies package-owned
stock driver selection for each installed kernel and checks boot integrity.
It leaves Wi-Fi calibration and the suspend guard installed. It does not reload
the running driver. Reboot to use the stock driver; its Wi-Fi resume failures
may return. If an experiment record remains after an incomplete migration, the
script stops so the backup and competing overrides can be reviewed first.

DKMS behavior is documented in the [upstream project](https://github.com/dkms-project/dkms).
Raw hardware reports and build artifacts remain ignored by the public repository.

The installer can retry an interrupted migration when the same package version is already installed and its DKMS source is package-owned. The checker accepts DKMS saved modules compressed with zstd, xz or gzip as well as uncompressed modules. Package installation can trigger the standard Limine UKI rebuild hook; the final integrity check verifies its updated hashes.

Post-migration validation on 2026-10-10: after reboot, installed/running module
and boot-integrity checks passed. Normal suspend completed with firmware reprobe;
the user confirmed working Wi-Fi and Touch Bar afterward on 7.2.5-3-omarchy.
