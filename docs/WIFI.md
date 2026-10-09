# BCM43602 weak reception · tested NVRAM candidate

## Findings on MacBookPro13,2

Initial Wi-Fi connectivity worked with the kernel brcmfmac driver, but reception
was unusually weak near an access point. The adapter is BCM43602, PCI 14e4:43ba,
Apple subsystem 106b:0157, firmware 7.35.177.61. Omarchy already disabled power
saving and configured feature_disable=0x82000. No BCM43602 NVRAM text file was
installed; the current interface MAC used the Broadcom placeholder prefix.

A community board-configuration candidate was installed under the model-specific
filename `brcmfmac43602-pcie.Apple Inc.-MacBookPro13,2.txt`. Only its macaddr field
was personalized with the original Wi-Fi MAC obtained from macOS. The complete
personalized file is deliberately not included in this public repository.

| Measurement | Before | After cold boot |
| --- | --- | --- |
| Exposed bands | Band 1 only | Band 1 and Band 2 |
| Connected frequency | 2437 MHz / 2.4 GHz | 5200 MHz / 5 GHz |
| Reported signal | -94 dBm | -49 dBm |
| RX link rate | 1 Mbit/s | 360 Mbit/s |
| TX link rate | 1 Mbit/s | 121.5 Mbit/s |
| Power saving | Off | Off |
| Global regulatory domain | NO | NO |
| PHY regulatory domain | 99 | 99 |

An earlier pre-test sample was -89 dBm at 2462 MHz, RX 39 / TX 104 Mbit/s.
The user confirmed working Wi-Fi and apparently better reception after cold boot.
The same location was requested, but exact positioning/AP identity was not
independently recorded. The band changed, and the candidate contains RSSI
compensation values: the signal delta is not a controlled antenna-gain measurement.
Link rates are negotiated PHY rates, not measured application throughput.

No firmware binary patch, country-code override, driver-option change, NetworkManager
change or UKI modification was made. A read-only UKI inspection showed no brcmfmac
module or BCM43602 firmware in its initramfs. The model-specific root-filesystem
text override was picked up after cold boot. This result does not imply every
installation can skip initramfs handling.

## Candidate provenance and limits

The candidate came from nohzafk/omarchy-macbookpro-t1 at commit 8e479f0,
`firmware/brcmfmac43602-pcie.txt`, with provenance pointing to
[MikeRatcliffe's gist](https://gist.github.com/MikeRatcliffe/9614c16a8ea09731a9d5e91685bd8c80).
Related weak-reception reports exist in
[DeyAgrO/macbook-pro-13-2-linux](https://github.com/DeyAgrO/macbook-pro-13-2-linux).

Boardtype 0x61b, boardrev 0x1421 and three-chain antenna settings have not been
independently verified as the exact board calibration for this machine. The
candidate retained its existing ccode/regrev, power and RF settings. A working
link does not establish exact calibration or regulatory suitability. Do not
copy another machine's MAC, blindly install a bundled multi-fix script, override
country limits or assume this file suits every BCM43602 board.

## Set up a new MacBookPro13,2

This repository now supplies `scripts/wifi`; no private experiment directory or
second community repository checkout is required. The template is downloaded
from the exact upstream commit above, and SHA256 must equal:

```text
b109f3e6663b0e888c2559e36f7e0109f2a3a6b9765786d11f849f16d4b32d06
```

The public repository does not redistribute the third-party RF calibration file.
Review [the pinned candidate](https://github.com/nohzafk/omarchy-macbookpro-t1/blob/8e479f0af82d16f47de811bef6e1a5cfd7d8c5f8/firmware/brcmfmac43602-pcie.txt)
and the provenance/limits above before installing it. Only the `macaddr` field
can change; modified RF settings or a changed upstream download are rejected.

Prerequisites on the recorded Omarchy layout: Python, `iw`, `binutils`
(`objcopy`), `mkinitcpio` (`lsinitcpio`), and the installed `limine-mkinitcpio`
integration. `scripts/boot-integrity` must accompany `scripts/wifi`. The hardware
must be MacBookPro13,2 with the Apple BCM43602 PCI identifiers above.

1. Obtain this machine's original Wi-Fi MAC in macOS System Information → Wi-Fi.
   Hold Option while powering on to use Apple's boot picker if macOS has no
   Limine menu entry. Use the Wi-Fi hardware address, not a Bluetooth address,
   randomized/private network address or Linux's Broadcom placeholder.
2. Save a baseline from the same position near the AP:

   ```bash
   mkdir -p reports
   sudo ./scripts/wifi status | tee reports/wifi-before.txt
   ```

   Status omits SSID/AP addresses and does not display your MAC. Review reports
   before sharing; they still contain local link/regulatory observations.
3. As your normal user, prepare a personalized candidate:

   ```bash
   ./scripts/wifi prepare
   ```

   The hidden prompt asks for the original Wi-Fi MAC. The exact template is
   fetched over HTTPS with a fixed checksum, and the personalized file is created
   with mode 0600 at ignored `build/wifi/candidate.txt`. It never overwrites an
   existing candidate. For offline preparation, supply the exact unpersonalized
   template explicitly with `--source /path/to/brcmfmac43602-pcie.txt`; the same
   checksum is required. Download that file on another machine if needed.
4. Review the locally prepared file. Have the checkout, rollback instructions
   and preferably an alternate connection available locally before installing:

   ```bash
   sudo ./scripts/wifi install build/wifi/candidate.txt
   ```

   Installation refuses existing model-specific or generic NVRAM overrides,
   including compressed variants. It creates only the model-specific firmware
   text file and private recovery metadata/copy, and installs persistent checks.
   It changes no firmware binary, country limits, driver options or NetworkManager
   settings. It does not reload Wi-Fi or reboot.
5. Cold boot when ready. Repeat `status` from the same position, test real network
   traffic, and record the result:

   ```bash
   sudo ./scripts/wifi status | tee reports/wifi-after.txt
   sudo ./scripts/wifi check --boot
   ./scripts/record-test wifi passed --notes 'Both bands exposed; connection and transfer tested after cold boot'
   ```

   Record a pass only after performing the stated tests. Compare the same
   AP/band/location for signal and throughput comparisons. The script does not
   automatically certify connectivity or join a network.

## Register this machine's already-working experiment

Do not reinstall or replace its existing working NVRAM file. From this checkout:

```bash
sudo ./scripts/wifi adopt
sudo ./scripts/wifi check --boot
```

Adoption validates the existing file against the pinned template, accepts only
its personalized MAC field, refuses package-owned files, saves a private recovery
copy and registers persistent upgrade checks. It leaves the firmware file's bytes
and timestamp unchanged. On the recorded machine, with no early Wi-Fi in the
initramfs, it also leaves the UKI unchanged. The original private experiment
record can remain as historical evidence; no script uses it to supply another
machine's MAC. Public adoption was subsequently run successfully on the recorded
host, with unchanged firmware and UKI and persistent validation installed.

## Boot images and recovery

Before install/adoption, the script verifies Limine's current UKI hash and safely
inspects the `.initrd` section using a separate `objcopy` output. A mismatch must
be repaired with `scripts/boot-integrity --repair` before proceeding.

If early Wi-Fi modules/firmware are present, the script creates its own
`/etc/mkinitcpio.conf.d/macbookpro13-2-wifi.conf` using `FILES+=` to include the
model-specific candidate. It then invokes the supported backed-up UKI rebuild
and checks both the boot hash and the actual embedded candidate's checksum.
Existing unrelated drop-ins are preserved. The tested machine does not need this
path today; its automated tests use simulated early-boot conditions.

If a later upgrade begins loading Wi-Fi early and the upgrade check reports a
missing/stale embedded candidate, run:

```bash
sudo ./scripts/wifi sync-boot
```

This includes the registered file in the initramfs and rebuilds/verifies through
Limine. It refuses to overwrite an existing unregistered or modified drop-in.
The helper supports only the recorded `/boot` Omarchy UKI layout; other layouts
need separate integration. See [BOOT-INTEGRITY.md](BOOT-INTEGRITY.md).

To undo this candidate:

```bash
sudo ./scripts/wifi rollback
```

Rollback deletes only a file matching the private installation record and removes
only its checksum-matching managed drop-in, if one was created. It rebuilds and
verifies the UKI when early-boot data is affected. It leaves packaged firmware
binaries and other overrides alone. The hook becomes inactive; the private
recovery copy and installed helpers remain available. Cold boot afterward.
If a rebuild fails, preserve the record/copy/log and resolve the failure before
rebooting; a pending rollback can be retried. A modified/missing untracked file
requires investigation rather than forced deletion. A completed rollback can be
reinstalled from the retained `candidate.txt` using `install` from the checkout.

## Persistent upgrade checks

Installation/adoption places root-owned copies of `wifi` and `boot-integrity`
under `/usr/local/lib/macbookpro13-2-omarchy`, so checks do not depend on this Git
checkout remaining in place. The pacman hook
`/etc/pacman.d/hooks/99-macbookpro13-2-wifi-check.hook` checks after firmware,
kernel and initcpio package changes, after the normal Limine image-building hook.
It verifies the on-disk candidate, managed drop-in, Limine hash and embedded
candidate when Wi-Fi is present in the initramfs. It never downloads/reinstalls
firmware, reloads a driver or silently replaces a checksum.

The firmware file is still a local override rather than a pacman-owned package.
Ordinary package updates leave differently named local files alone, but a future
package claiming the same path needs explicit migration. A failing post-transaction
hook cannot undo a package transaction. Inspect its output before rebooting.
Update installed helper copies deliberately from a reviewed checkout:

```bash
sudo ./scripts/wifi update-checks
```

The integrated pre-reboot check also includes Wi-Fi:

```bash
sudo ./scripts/check-upgrades
```

A missing installation record is reported as unmanaged, not as a functional pass.
Private candidates, MAC addresses, reports and `/var/lib` recovery copies must
stay out of the public repository. No Apple firmware/EFI backup is distributed.

## Remaining verification and maintenance

Measure repeatable LAN throughput to a trusted wired host (for example with iperf3),
packet loss and longer connection stability. Repeat cold boots and test suspend
separately. Compare the same AP/band/location when quantifying improvements.
Do not conclude that a better displayed RSSI alone proves better RF performance.

After kernel/firmware updates, run the integrity/status checks and verify both
supported bands and actual connectivity. Checksum validation does not establish
that a changed driver selected this override or that new kernel behavior is correct.

A subsequent suspend attempt failed the Wi-Fi D3 handshake and left Wi-Fi
unusable. See [SUSPEND.md](SUSPEND.md); the NVRAM improvement does not solve this
power-management failure.
