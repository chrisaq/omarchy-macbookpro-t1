# Repository validation

On 2026-10-09, without installing drivers or changing services/boot configuration:

- The status collector ran on MacBookPro13,2 and produced a JSON inventory.
- It detected normal-mode T1, configuration 1, correct HID bindings and Touch Bar
  control values. It still classified hardware as detected without local test records.
- The upgrade check passed installed builds for 7.2.5-3-omarchy; it correctly noted
  the standalone Touch Bar package check was unavailable on the manual deployment.
- Audio preparation exported the pinned local upstream commit and applied the
  DKMS patch successfully in an ignored workspace directory.
- Tests verified detection cannot become a functional pass, older-kernel results
  remain distinct, records survive round-tripping, and an audio pre-build that
  returns success without source is rejected.
- Script syntax and local documentation links were checked.

The audio install script, playback/recording/camera tests and suspend were not run.
The patched audio recipe has not been compiled/installed here. It must be tested
on a planned fresh installation before marking it runtime-verified. The original
upstream audio installation and manual Touch Bar fix have the historical evidence
in INSTALLATION-RECORD.md.

The GitHub workflow checks Python tests and shell scripts. It has not run on GitHub
and cannot verify physical hardware. No public repository was created or published
by this task.

The boot-integrity revision adds five tests covering correct BLAKE2b hashes,
missing/malformed/stale/SHA-512 hashes, conflicting duplicate references,
unsupported layouts and refusal to repair a fixture root. All 12 tests passed.
On the host, the user ran the read-only checker and confirmed a real mismatch,
then ran `boot-integrity --repair`: the installed Limine workflow rebuilt the
UKI, updated the entry and passed both hash and embedded-kernel checks.
The user subsequently confirmed the warning was gone after reboot. The revised audio installer itself was not run.

## Public Wi-Fi scripts

The public Wi-Fi workflow pins the tested upstream template by full commit and
SHA256 and personalizes only its MAC field. The local template checksum and the
existing installed candidate were verified without displaying the MAC. The pinned
HTTPS download could not be exercised in the restricted development environment;
local-source preparation is supported with the same checksum.

All 22 repository tests passed, including Wi-Fi personalization/privacy, rejected
modified RF settings, invalid MACs, preserved existing overrides, install/check/
rollback, adoption without rewriting, early-boot inclusion and retained recovery
state on build failure. Early-boot behavior was simulated; the recorded machine's
UKI contained no early Wi-Fi. The user subsequently ran public `wifi adopt` successfully on the host: the
existing candidate was registered without rewriting it, the UKI hash remained
valid, early Wi-Fi remained absent, and the persistent validation hook was
installed. Installed helper and hook contents match the repository copies.
Public fresh installation/rollback and an actual pacman-triggered check have
not yet been exercised on this host; early-boot handling remains simulated.
The original private installation and cold-boot Wi-Fi improvement remain the
functional evidence in WIFI.md.
