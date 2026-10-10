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

Suspend persistence adds six fixture tests for expected topology and exclusion
of Wi-Fi's root, rejected PCI/USB/storage peripherals, missing controller refusal,
retained recovery markers on partial preparation and required unit ordering/cleanup.
All 28 tests passed. Unit parsing passed with placeholder executable paths during
offline verification. The user installed the real helper and tested normal
`systemctl suspend`: preparation, cleanup and restoration of all expected
Thunderbolt controllers succeeded. Wi-Fi firmware commands timed out after
wake, so persistence is **not a validated complete suspend fix**. Three earlier
foreground subtree-cycle tests bypassed normal logind/NetworkManager sleep
notification and cannot establish ordinary suspend or lid-wake reliability.
The subsequent `suspend-test normal` diagnostic cycle used the normal logind
path and a 20-second RTC alarm. The user confirmed automatic wake and working
Wi-Fi/Touch Bar; firmware reinitialized during resume and all Thunderbolt
controllers returned. This is one successful normal diagnostic cycle alongside
one failed ordinary cycle, not evidence of reliable suspend or lid wake.
The second normal diagnostic cycle (20261010T030837Z) also returned 0 with fresh
Broadcom firmware initialization and user-confirmed Wi-Fi/Touch Bar operation.
The earlier ordinary-suspend failure remains unresolved; debug logging, timed
wake and sleep duration differ from that failed cycle.
An ensuing ordinary `systemctl suspend` cycle, without requested diagnostic
logging or an RTC alarm, also passed: the user confirmed Wi-Fi/Touch Bar, and
the journal confirms firmware initialization and full controller restoration.
Entry/exit spanned 05:11:19–05:14:03 (2026-10-10); collection report
20261010T031431Z. Lid wake, peripheral use and long-term stability remain untested.
The ensuing lid-close trial restored Wi-Fi, Touch Bar and trackpad after a
brief power-button wake, but opening the lid did not wake the machine. Lid
wake therefore failed this trial; device recovery passed. The new
`test-lid-wake` diagnostic passed shell syntax checking only.
The logging-only diagnostic subsequently ran and again required power-button
wake. Its temporary `--ec-wake` comparison also required power-button wake;
Wi-Fi and Touch Bar worked afterward and original EC policy was restored.
Enabling EC wake is therefore not a demonstrated lid-wake fix.

The experimental BCM43602 reprobe patch subsequently compiled against the exact
kernel headers, was installed without changing stock driver/UKI, and was confirmed
loaded after reboot. Two RTC diagnostic cycles explicitly selected the patched
resume path and reinitialized firmware. Wi-Fi/Touch Bar/trackpad passed the user's
functional check after the repeat. Ordinary suspend with this candidate, lid wake,
rollback execution and upgrade persistence remain unvalidated.
The user subsequently confirmed all three devices after ordinary candidate
suspend and after a lid-close/power-button-wake trial. Lid opening alone still
failed to wake the machine. Candidate runtime evidence now includes two timed
cycles and those two ordinary trials; rollback and upgrade persistence are still
pending, and long-term stability/battery drain are not established.

## Wi-Fi DKMS post-reboot validation — 2026-10-10

After migration to mbp13-2-brcmfmac-dkms 7.2.5.1-1 and reboot on
7.2.5-3-omarchy, the package checker confirmed selected DKMS module, running
patched source and matching UKI/Limine hashes. The normal suspend test
(report timestamp 20261010T111900Z) completed successfully: the model-specific
firmware reprobe ran, firmware initialized, and the Touch Bar resumed. The user
confirmed Wi-Fi and Touch Bar worked afterward. Touchpad operation was confirmed
in earlier tests but was not separately confirmed for this cycle. Wake source
was not independently confirmed by the user. Lid wake, long sleep, battery drain
and compatibility with future kernels remain unverified or unresolved.
