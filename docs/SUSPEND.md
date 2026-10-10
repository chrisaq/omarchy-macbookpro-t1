# Suspend failure: Wi-Fi timeout and Touch Bar resume

> **Current status, 2026-10-10:** The installed Thunderbolt guard and patched
> Wi-Fi driver restored Wi-Fi, Touch Bar and trackpad across repeated tests.
> Wi-Fi DKMS migration succeeded and module selection/UKI integrity passed;
> post-migration reboot and normal suspend confirmed Wi-Fi and Touch Bar. Lid opening still requires a
> brief power-button press. Long sleep, battery drain and attached peripherals
> remain unverified. See [Wi-Fi package instructions](WIFI-RESUME.md).

The following investigation is chronological; failed and superseded experiments
are retained as evidence, not as the current installation procedure. Start with
[the persistent configuration](#persistent-configuration-and-lid-testing) and
[the Wi-Fi DKMS package](WIFI-RESUME.md).

## Normal suspend regression after installing persistence

The first normal `systemctl suspend` test at 22:11 on 2026-10-09 selected
`s2idle` and returned. The required guard prepared both Thunderbolt trees and
restored all expected controllers/drivers afterward; its lifecycle completed
correctly. Nevertheless, Broadcom firmware queries began timing out immediately
after wake, followed by channel, transmit-power and scan failures (`-5`). The
user reported unusable Wi-Fi and subsequently rebooted.

The earlier successful foreground tests started `systemd-suspend.service`
directly. They did not exercise the normal logind `PrepareForSleep` path.
During the failing normal test, NetworkManager disconnected and unmanaged Wi-Fi
before sleep, then tried to manage it again after wake. This difference is an
investigation lead, not proof that NetworkManager caused the failure.
Earlier successful cycles logged fresh Broadcom firmware initialization on
resume; this failing cycle did not. The upstream
[PCIe driver](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/broadcom/brcm80211/brcmfmac/pcie.c)
has both a hot-resume path and a remove/probe fallback. Which path this installed
kernel took needs callback/driver diagnostics; do not assume a successful PCI
resume return means the firmware answers commands.

The guard's `check` verifies Thunderbolt topology only. It does not test Wi-Fi
connectivity. No Wi-Fi driver reload, firmware edit or NetworkManager workaround
has been added in response. Avoid further ordinary/lid suspend until a controlled
comparison is prepared. If removing the experimental installation, use
`sudo ./scripts/disable-suspend`; the restored previous deep-sleep policy is also
known to fail, so rollback does not make suspend reliable.

### Next diagnostic comparison

After rebooting and confirming ordinary Wi-Fi works, save work, disconnect
peripherals and leave the lid open:

```bash
sudo ./scripts/suspend-test normal
```

This mode requires the installed guard and checks its integrity/topology first.
It temporarily enables kernel PM callback logging, selects s2idle and arms a
20-second RTC wake. It invokes normal `systemctl suspend`, including logind's
NetworkManager notification, then observes completion without enqueueing a
second suspend. It saves kernel and service logs in the printed private report
directory and restores temporary debug/sleep/alarm settings on return. Raw
service logs can contain network identifiers; review before publishing.

This is a diagnostic reproduction of a known failure, not a fix. Wi-Fi may fail
again, and a kernel hang can require reboot. Keep the report locally even if
internet is unavailable. The new mode passed shell syntax checks; existing
28 fixture tests passed, but do not exercise real sleep or the new runtime wait.

The first `normal` diagnostic run (20261009T202549Z) returned status 0.
Wall-clock suspend entry/exit spanned 22:25:51–22:26:11, consistent with timed
wake. Broadcom performed fresh firmware initialization and renamed its new
interface during resume; its callback returned 0 in about 666 ms. Thunderbolt
cleanup restored all expected controllers, and the Touch Bar logged resume.
No repeated firmware-command timeouts appear in the inspected subsequent log.
The user confirmed automatic wake and working Wi-Fi and Touch Bar afterward. This
successful diagnostic path means normal NetworkManager sleep notification alone
does not consistently reproduce the failure. RTC versus manual wake, elapsed
sleep time, debug logging/timing and prior device state remain uncontrolled
differences; no cause or reliable Wi-Fi fix is established.

The second `normal` diagnostic run (20261010T030837Z), requested without a
reboot between diagnostic cycles, also returned status 0. Broadcom reinitialized
firmware again (resume callback about 668 ms), noirq resume took 233 ms, and the
user confirmed Wi-Fi and Touch Bar working. Automatic-wake confirmation for this
second cycle was not explicitly supplied. Two passing RTC/debug cycles still
do not reproduce the earlier ordinary-suspend Wi-Fi failure or validate lid wake.

The subsequent ordinary `systemctl suspend` test also passed with user-confirmed
Wi-Fi and Touch Bar operation (collection report 20261010T031431Z). No diagnostic
RTC alarm or callback logging was requested for that test. The journal shows
entry at 05:11:19 and exit at 05:14:03 on 2026-10-10, fresh Broadcom firmware
initialization, Touch Bar resume, and complete Thunderbolt restoration by
05:14:06. Thus debug logging/RTC wake are not required for every successful
cycle. The earlier Wi-Fi failure remains unexplained; lid wake is the next
separate validation step with peripherals disconnected and work saved.

The lid-close trial (collection 20261010T032017Z) suspended and returned with
Wi-Fi, Touch Bar and trackpad working, but opening the lid did not wake it;
a brief power-button press was needed. `LID0`/PNP0C0D wake policy is already
enabled. EC wake policy is disabled, while `acpi.ec_no_wakeup` is `N`; these
settings alone do not establish the cause. logind recorded lid close at
05:17:53 and lid open at 05:19:48, near resume. An event recorded at resume
does not prove it triggered wake rather than being processed after button wake.

For a single lid-specific diagnostic cycle, run `sudo ./scripts/test-lid-wake`.
It verifies the installed guard, enables temporary PM callback/wakeup logging,
records lid/EC wake counters and waits in the terminal while the user closes
and opens the lid. It does not request suspend itself, arm an RTC alarm or
change wake policy. After opening, wait 15 seconds; if necessary use one brief
power-button press. Press Enter in the waiting terminal only after returning
to collect logs and restore debugging. Interrupting the script also restores
debug settings; a kernel hang can prevent cleanup until reboot. No EC/LID
wake-policy change has been tested or made persistent. Script syntax passed;
this new diagnostic's runtime remains untested.

The logging-only lid test (20261010T032449Z) again needed a power-button press;
the user confirmed devices still working afterward. The log shows IRQ 9 / an
ACPI fixed-event wake, consistent with the reported button wake. Lid wake has
therefore failed twice, despite enabled LID0 wake policy.

The next isolated comparison is `sudo ./scripts/test-lid-wake --ec-wake`.
It requires the observed disabled EC wake policy and `ec_no_wakeup=N`, enables
only the EC's sysfs wake policy for the user-triggered lid test, and restores
its original value when the terminal test finishes or is interrupted. Before,
test-time and restored wake settings are saved privately. Enabling a wake source
can also cause unwanted/immediate wake; report that outcome rather than treating
it as successful lid wake. This comparison is untested, and no permanent EC
configuration has been installed. A kernel hang can prevent script cleanup;
the runtime-only setting is reset on reboot.

The EC-enabled comparison (20261010T032850Z) did not fix lid wake: the user
still needed a power-button press, with Wi-Fi and Touch Bar working afterward.
The helper restored the original EC wake setting. The log again shows a fixed
ACPI event wake. Do not install a persistent EC-wake rule based on this test.
Further investigation should inspect firmware ACPI lid notification/wake
methods rather than repeat the same unsuccessful wake-policy comparison.
`sudo ./scripts/collect-lid-acpi` copies only DSDT/SSDT executable firmware
tables and current wake policy into an ignored, private checkout report directory
owned by the invoking regular user, for offline inspection. It does not load or
patch ACPI tables, install software or change system settings. Review captures
before sharing. Capture-script syntax passed; firmware capture remains pending.

The user captured DSDT and 11 SSDTs (lid-acpi-yWhC4Mgj). Raw AML inspection
locates `LID0._PRW` and `_PSW`, with the latter writing an EC field named
`EWLO`. This is an analysis lead, not proof of a firmware defect or a reason
to write EC registers. Full method/context decoding remains pending because
`iasl` is not installed. Install Arch's `acpica` package, then run
`./scripts/decode-lid-acpi /path/to/capture` as the regular user. It uses SSDTs
as external declarations and disassembles DSDT offline; it never executes or
loads AML. Source AML is preserved and decoded/private files remain ignored.

### Decoded firmware findings

Offline decoding succeeded. `LID0._PRW` advertises wake GPE `0x6f` (S4 on
the Darwin branch, S3 otherwise). `LID0._PSW(1)` sets the EC's `EWLO` bit,
provided `ECOK` is true; `_PSW(0)` clears it. The EC query `_Q20` reads `ELSW`
and issues `Notify(LID0, 0x80)`. `_L6F` acknowledges chipset register status
but does not itself notify the lid device. `_PTS` writes the EC sleep-state
field `ECSS`; `_WAK` resets it. These are firmware mechanisms, not proof of
which methods actually executed during the failed s2idle trials.

Linux's [ACPI s2idle preparation](https://github.com/torvalds/linux/blob/master/drivers/acpi/sleep.c)
arms wake devices for S0 through a different path from firmware S3 suspend.
Consequently, an enabled sysfs wake policy alone does not establish correct
firmware lid arming or notification delivery on this host. The next useful
investigation is tracing actual wake preparation and ACPI notification delivery,
including whether the lid's wake-enable method runs. Do not directly write EC
registers, force `_PTS(3)` during s2idle, spoof the OS or load modified AML
based only on this offline analysis. No lid-wake patch is established.

Current practical limitation: with the installed peripheral-free s2idle guard,
recent lid-close trials restored devices after a brief power-button wake;
opening the lid alone did not wake them. The earlier Wi-Fi failure remains
an unresolved exception. Deep sleep is still unvalidated and previously hung;
changing back to deep is not a demonstrated lid-wake solution.

### Trace actual lid wake preparation

Run `sudo ./scripts/test-lid-wake --trace` for one instrumented lid cycle.
This uses a private tracefs instance and uniquely named temporary kprobes for
ACPI object evaluation (`_LID`, `_DSW`, `_PSW`), simple `_PSW` calls with their
enable/disable argument, and the lid notification handler. `_LID` handle values
allow matching the lid with wake-method calls without assuming a device pointer
layout. A call entry shows an attempted evaluation, not necessarily successful
execution or the resulting EC register value. No return values are recorded.
Optional suspend/resume trace events provide phase boundaries. The boot trace
clock is selected when available so elapsed sleep can be distinguished; the
selected clock and per-CPU loss/overrun stats are saved with the trace.

The test leaves EC/LID wake policy unchanged, uses the installed sleep guard,
and follows the same close/open/wait/button-if-needed instructions. After Enter,
it saves the private trace, disables/removes only its own instance/probes and
restores debug settings. Other probes and global trace buffers are preserved.
It stops before the requested lid test if probe setup fails. Raw trace contains
kernel handle addresses and is private; review before publication. A reboot
clears runtime probes if a hang prevents cleanup. Function signatures were
checked against upstream source and symbol names against the running kernel;
shell syntax passed, but root probe registration and tracing await host testing.

The first trace setup was rejected (`EINVAL`) before sleep. The original
probe tried fetching a string directly from an argument; the revised x86_64
definition dereferences the second argument register with `+0(%si):string`.
Argument registers `%di`/`%si`/`%dx` supply the first three parameters. Before
requesting any lid cycle, the script reads lid state and requires a decoded
`_LID` evaluation in its trace. `--trace-check` performs only this setup/read/
cleanup, with no suspend or debug-policy change. Kernel trace setup errors
are saved privately when available. Shell syntax passed; corrected root
registration remains pending. Follow the successful preflight with `--trace`.

Corrected trace preflight succeeded (20261010T034153Z), decoding a live lid
state read and removing its probes. The subsequent actual trace
(20261010T034347Z) reproduced Wi-Fi failure; the user corrected the initial
all-hardware-working report to Touch Bar working, Wi-Fi not working. The first
sleep at 05:44:00 woke at 05:44:03 on a non-EC GPE, while the lid was still
closed; another sleep started at 05:44:31 and ended at 05:45:00 with an ACPI
fixed-event wake. Which physical action woke this trial was not explicitly
confirmed. Do not interpret logind's lid-open line as proof of lid wake.

Both Broadcom resume callbacks returned 0 in about 46–51 microseconds with
no fresh firmware initialization, unlike roughly 666–668 milliseconds and
firmware initialization in successful diagnostic cycles. Repeated command
timeouts appeared after the second wake. This implicates investigation of the
driver's hot-resume path; it does not establish the cause or justify installing
an automatic reload workaround. The user rebooted afterward. Full trace/loss
stats must be examined before asserting missing lid wake-method calls, since
the terminal printed only a tail. `export-suspend-trace` copies selected trace
files into a private ignored checkout directory for offline inspection without
altering the root-owned originals or sleep/wake settings.

Full trace inspection (offline copy suspend-trace-HjGRO6Zm) found zero per-CPU
overruns/dropped events. Matching the lid's `_LID` handle establishes attempted
`_PSW(1)` evaluations before both sleeps and `_PSW(0)` afterward. Missing
wake-enable invocation is therefore not the explanation supported by this
capture; method return status and actual EC flag contents remain unmeasured.
The second `machine_suspend` interval lasted about 27 seconds on the boot
clock. Its lid notification (`0x80`) arrived about 21 ms after that interval
ended. The user explicitly confirmed every lid-close trial required the power
button. This is consistent with notification being processed after button wake,
not evidence of successful lid wake. No firmware/EC patch has been installed.

Prioritize the independently recurring Broadcom failure before further lid
experiments. Both Wi-Fi resumes in this capture skipped firmware reinitialization
and returned in microseconds, followed by command timeouts. A tested solution
must cover that hot-resume case as well as the already passing firmware-reprobe
case. The trace test removed its probes; the original root-owned reports and
private offline copy are retained.

### Experimental Wi-Fi driver candidate (not installed)

`patches/brcmfmac-mbp13-2-cold-resume.patch` bypasses the hot-resume branch
only for Apple Inc. MacBookPro13,2, BCM43602 and the observed PCI/subsystem IDs
14e4:43ba / 106b:0157. It uses the existing cleanup/remove/probe resume path
and logs that the experimental quirk was selected. This tests the distinction
seen in local failures; it is not a proven fix and does not fix lid wake.
It changes neither firmware/NVRAM nor other adapters' resume policy.

The running kernel is 7.2.5-3-omarchy. The historical
[Omarchy recipe](https://github.com/omacom/omarchy-pkgs/blob/7b11c97603dd9d751d803746560ee51640709725/pkgbuilds/linux-omarchy/PKGBUILD)
matches 7.2.5-3; today's recipe does not. Run
`./scripts/prepare-wifi-resume-source` without sudo to fetch that pinned recipe
and accompanying patches for review. This step does not execute the recipe.
Development network DNS prevented fetching sources here. Patch format and
script syntax were checked, but application to exact sources, compilation,
reversible installation and upgrade integration remain pending. Do not manually
replace the stock module or install this candidate yet. A reproducible build
and rollback must precede testing; persistence is appropriate only after tests.

The user fetched the pinned historical recipe successfully. None of its
accompanying patches refers to the Broadcom brcm80211 subtree. The build-only
step is `./scripts/build-wifi-resume` without sudo (an existing
`linux-7.2.5.tar.xz` may be supplied as its sole argument). It verifies the
recipe commit/version and the kernel archive's pinned BLAKE2b checksum, refuses
vendor Broadcom changes requiring review, extracts only Broadcom source, applies
the experimental patch with no fuzzy context, and compiles against installed
7.2.5-3-omarchy headers/Module.symvers. It retains the parent Makefile's debug
flags; brcmutil/brcmsmac are excluded from the build. Firmware-vendor helper
modules may be built as dependencies, but nothing is installed.

The build records source/patch/module/header checksums and checks module vermagic.
It refuses another kernel release or existing candidate staging. Python syntax
passed; exact-source patch application and compilation await the user's networked
build. A successful compile is not runtime validation. Review the result before
writing an installer/rollback; neither loading nor upgrading this experimental
module is authorized by running this build-only command.

The first build attempt rejected the resume hunk because its context came from
newer upstream source. The patch was regenerated against the checksum-verified
7.2.5 archive, then applied without offsets/fuzz. Incomplete staging is now
renamed and preserved on retry; completed build records are protected. Local
compilation subsequently succeeded for brcmfmac and vendor helpers against
7.2.5-3-omarchy headers, including modpost and BTF. The module's vermagic matches
and its build record contains source/patch/module/Module.symvers hashes. This
is build validation only; no candidate has been loaded by that build.

### Reversible current-kernel experiment

After reviewing the candidate, install using
`sudo ./scripts/wifi-resume-experiment install`. The installer checks model/PCI
identity, recorded build hashes, vermagic, current stock module ownership,
signature restrictions, boot integrity and absence of early Wi-Fi in the UKI.
It refuses existing overrides or experiment state. It copies **only brcmfmac**
to the current kernel's `updates/macbookpro13-2-wifi/` directory and runs depmod,
verifying that the override is selected. Stock module and vendor helpers stay
in place; root-owned private state records their provenance/checksums. It never
reloads the running driver or alters/rebuilds the UKI. Reboot when ready to load
the candidate, then run `sudo ./scripts/wifi-resume-experiment check` and verify
normal connectivity/both bands before any suspend test.

Keep rollback locally: `sudo ./scripts/wifi-resume-experiment rollback` removes
only the recorded, checksum-matching override, reruns depmod and verifies stock
selection. Reboot to load stock. It preserves changed files for inspection rather
than deleting them. A pending removal can retry rollback if depmod failed after
the override was deleted. Script syntax passed; root install/rollback and
runtime suspend are pending. The unsigned external module may taint the kernel;
the installer refuses active lockdown/signature enforcement.

This is deliberately scoped to the recorded kernel, **not yet upgrade-persistent**.
Do not treat it as the new-machine Wi-Fi setup or perform kernel upgrades during
the experiment. If runtime validation succeeds, a reviewed DKMS/package workflow
with upgrade checks is the next step; if it fails, restore stock. Lid-wake
reliability and the firmware D3-handshake timeout are separate unresolved cases.

### First candidate runtime results

The user installed the current-kernel override; stock checksums and UKI integrity
passed. After reboot, `wifi-resume-experiment check` identified the running
candidate. Two normal-path RTC diagnostic cycles (20261010T040742Z and
20261010T041024Z) returned 0 and explicitly logged the model-specific firmware
reprobe quirk, followed by fresh firmware initialization. Resume callbacks took
about 667 and 676 ms. The user confirmed Wi-Fi, Touch Bar and trackpad working
after the repeat. The first wake may have coincided with keyboard contact;
automatic hands-off wake was requested for the repeat but not explicitly
confirmed in its response. These are initial positive results, not proof of
reliable ordinary/lid suspend or readiness for upgrade persistence.

Next compare ordinary `systemctl suspend`, without callback logging or an RTC
alarm, with peripherals disconnected and the lid open. Wake with a brief
power-button press after about a minute, verify hardware, then capture with
`sudo ./scripts/suspend-test collect`. Do not infer lid wake from device recovery.

The ordinary candidate test (collection 20261010T041513Z) entered kernel
`s2idle` at 06:12:57 and exited at 06:13:45, a roughly 48-second sleep
transaction. systemd froze/thawed user.slice and the guard restored controllers;
the patched Broadcom reprobe and fresh firmware initialization occurred during
resume. The user reported an immediate desktop return after touching the keyboard.
The journal establishes real kernel suspend, rather than screen blanking alone;
the exact wake IRQ was not logged in this non-debug cycle. Sleep power consumption
is not established by the timing or desktop responsiveness. Functional device
confirmation for this ordinary cycle remains pending.

The user subsequently confirmed Wi-Fi, Touch Bar and trackpad working after
that ordinary cycle. A following lid-close trial (collection 20261010T041902Z)
also restored all three, but required a power-button wake; opening the lid alone
still did not wake it. The Wi-Fi candidate has therefore passed two timed
diagnostic cycles, one ordinary keyboard-associated wake and one lid-close /
power-button-wake recovery trial. This is encouraging initial evidence for the
reprobe workaround, not a lid-wake fix or long-term stability/power assessment.
The latest journal again shows an early wake/re-suspend sequence: 06:17:05–
06:17:08 followed by 06:17:36–06:18:18. Both resumes selected the experimental
reprobe and reinitialized firmware, with no repeated firmware-command timeouts
in the inspected interval. Thus this trial also covers the double-cycle pattern
that previously ended with broken Wi-Fi; the source of the early wake remains
unidentified.

## Observed failure (2026-10-09)

After a lid/suspend attempt, the user reported that Wi-Fi and the Touch Bar were
unusable. The saved kernel log shows a failed suspend transaction, rather than
a successful sleep followed by a clean wake:

- The Touch Bar logged that it suspended.
- `brcmf_pcie_pm_enter_D3` timed out waiting for the Wi-Fi firmware's D3 handshake.
- PCI suspend returned `-5` (`EIO`), and the kernel aborted suspend.
- After unwinding, Wi-Fi commands repeatedly failed to reserve common-ring space
  and reported `-12`. This symptom alone does not establish exhausted system RAM.
- No Touch Bar resumed message appears in the supplied excerpt.

The user's selected memory sleep mode was `deep` in the subsequent read-only
inspection. The user had already recovered from the failed state before further
live diagnostics. Successful cold boots and ordinary Wi-Fi use remain established;
suspend/resume is now known to fail in this configuration.

## Touch Bar callback repair

The historical community driver registers `suspend` and `reset_resume`, but not
ordinary `resume`. Its suspend callback marks the interfaces suspended, disables
work and turns the bar off. An ordinary USB resume, including unwind after an
aborted suspend, therefore has no Touch Bar restoration callback. The iBridge
coordinator already forwards ordinary resume calls to a registered subdriver.

The public Touch Bar source now registers the existing restoration routine for
both `resume` and `reset_resume`. This is a small source-level repair, not a
post-resume reload. It compiled for `7.2.5-3-omarchy` and is included in package
revision `0.1-3`. Runtime suspend/abort recovery testing remains pending.

For the historical **unowned manual appleibridge/0.1 installation** on the
recorded host, the Touch Bar checkout has a targeted repair script:

```bash
sudo /path/to/apple-t1-touchbar/scripts/repair-manual-resume
```

It saves a private source backup, adds only the missing callback, force-builds
and installs that driver, then runs the supported backed-up UKI rebuild and
hash verification. It refuses package-owned source and never unloads/reloads
running Touch Bar modules. Reboot when ready to load the revised driver.
For a packaged installation, upgrade the reviewed Touch Bar package instead.
Do not run the historical manual persistence installer afterward: its older
source snapshot does not contain this callback repair.

An independent [MacBookPro13,2 runbook](https://gist.github.com/bgausden/c7f8a3737c1e52a260dfcdb1fb2e90b2)
also carries the ordinary-resume callback fix. Its other hardware workarounds
are separate changes and have not been adopted here.

## Wi-Fi investigation

The Broadcom failure needs a separate fix. The saved log identifies a firmware
power-state handshake timeout; improving reception with NVRAM does not establish
working suspend. No calibration/firmware file was changed in response to this log.

An [upstream brcmfmac patch](https://lists.openwall.net/linux-kernel/2026/09/15/57)
changes handling of a missing D3 acknowledgment when wake-on-wireless is disabled.
Its reported test platform uses BCM43752, not this BCM43602. That patch has not
been installed, and it must not be described as a verified fix for this Mac.
Do not apply unrelated T2/Apple-Silicon recipes or sweeping PCI/Thunderbolt changes
merely because their logs share a timeout message.

Before another controlled suspend test, boot the Touch Bar callback repair and
verify ordinary Wi-Fi and Touch Bar use. Collect the next failure state locally
using the read-only report:

```bash
sudo ./scripts/suspend-status > reports/suspend-status.txt
```

The report omits SSIDs, MAC addresses and kernel command-line identifiers. It
records sleep selection, PCI power state, HID bindings/controls, configured sleep
settings, existing sleep hook filenames and relevant kernel events. Collect it
before reboot if practical; it does not require working internet. Review reports
before publishing them. Do not repeatedly trigger a failing lid sleep or live
reload the Touch Bar as a recovery measure.

A future workaround must be separately tested for actual sleep, Wi-Fi reconnection
and both bands, Touch Bar restoration, clean shutdown and repeated cycles. Changing
only the sleep mode or restarting a userspace service is not yet a demonstrated
solution. No automatic suspend hook is installed by this investigation.

## Subsequent deep-sleep wake failure

A later lid suspend required forced power-off. Its persistent journal ends at
`PM: suspend entry (deep)` at 20:01:53 with no recorded resume or callback error.
This does not establish whether the failure occurred during entry, wake, or
before logging could restart. The manual Touch Bar source contains the ordinary
resume callback and its DKMS module was rebuilt at 19:50:32; the machine's next
boot started at 20:15. It is not yet confirmed that the repaired module had been
loaded during the failed 20:01 suspend; its preceding boot began at 19:41.

The new boot's PM trace hash matches `acpi device:83`, whose ACPI path is under
`RP09.UPSB.DSB4.UPS0.DSB4.UPS0.DSB4`, plus a memory node. These RTC-derived hashes
can collide or reflect older trace data; they suggest investigation of the
Thunderbolt topology but do not prove the responsible device. The existing
`omarchy-nvme-suspend-fix.service` sets NVMe `d3cold_allowed=0`, which is active.
No driver/device/configuration changes were made during this investigation.

Collect private previous-boot and current diagnostics:

```bash
sudo ./scripts/suspend-test collect
```

After saving work, with the lid open, the next isolated test is:

```bash
sudo ./scripts/suspend-test devices
```

This selects the kernel's `pm_test=devices` facility, enables temporary callback
logging, and runs the systemd suspend oneshot synchronously. The kernel should
suspend/resume devices after its built-in test delay without entering platform
sleep. A broken callback can still hang. The script restores runtime test/debug
settings after it returns; a reboot also resets them. It does not change boot
images, persistent sleep configuration, or driver bindings. Logs remain private
under `/var/lib/macbookpro13-2-omarchy/suspend-reports`.

If the device test hangs/fails, investigate device callbacks before real sleep.
If it returns and hardware remains functional, the next controlled comparison is
`s2idle` against `deep`; that real sleep test is not performed by this script.
Do not repeat uncontrolled lid tests while wake remains unreliable.
See the [kernel PM debugging guide](https://www.kernel.org/doc/html/latest/power/basic-pm-debugging.html).

## Device-only test result and next comparison

The user ran the device-only test after reboot. It returned exit status 0,
completed device resume in about 555 ms and reported that Wi-Fi, Touch Bar and
the desktop all seemed functional. The journal contains both Touchbar suspended
and resumed messages. This validates one callback round trip, not real sleep or
repeated reliability. It narrows the next investigation toward the deeper
platform sleep/wake path; intermittent driver failures remain possible.

The script now offers a real, temporary s2idle comparison:

```bash
sudo ./scripts/suspend-test s2idle
```

Save work and keep the lid open. It uses a temporary `/run/systemd/sleep.conf.d`
override, selects s2idle and arms an RTC alarm for approximately 20 seconds. It
refuses to replace an existing alarm/test override or run with PM trace active.
Wake is not guaranteed if the kernel/firmware fails. Upon return, the script
removes its override/alarm and restores the previous runtime sleep/debug settings.
A reboot clears the temporary override too. No UKI or persistent sleep setting
changes. The private report retains before/after diagnostics. This real s2idle
comparison has not yet been run; do not mark suspend fixed based on the callback
test alone. After return, check normal desktop operation, Wi-Fi connectivity and
both bands, Touch Bar and audible audio before testing lid wake separately.

## Real s2idle result: Thunderbolt resume stalls

The real s2idle test returned normally and the user confirmed working Wi-Fi and
Touch Bar, but it appeared asleep until the user held the power button for several
seconds. The actual log records s2idle, IRQ 9 / ACPI fixed-event wake, and then
**81.663 seconds in noirq device resume**. Both Alpine Ridge USB controllers
(`06:00.0`, `7c:00.0`) timed out repeatedly through 65535 ms. Their parent bridges
reported D3cold-to-D0 inaccessibility; both Thunderbolt NHI functions also failed
readiness checks. The current PCI tree no longer shows the two USB controllers,
and the NHI functions remain in D3cold. This is a failed controller recovery, not
a successful general suspend workaround merely because Wi-Fi and Touch Bar work.
The RTC may have triggered wake at the intended time; the subsequent resume delay
is consistent with the user-observed long wait. IRQ 9 alone does not distinguish
the RTC event from the power button.

The next staged comparison is a runtime-only D3cold restriction on the exact
internal Thunderbolt topology:

```bash
# Reboot first to recover the missing USB controllers; disconnect peripherals.
sudo ./scripts/suspend-test s2idle-no-d3cold
```

The script verifies all 16 internal Intel PCI IDs before writing settings and
refuses missing controllers or additional PCI endpoints in those trees. It sets
only their `d3cold_allowed` flags to zero for this one s2idle/RTC test, saving and
restoring the prior values. It does not remove/rescan/unbind devices or alter
NVMe/Wi-Fi/T1 power policy. Disconnect USB-C/Thunderbolt peripherals first; the
PCI endpoint guard does not detect ordinary USB devices. Runtime restrictions
can increase power consumption during this test. A reboot resets them if a hang
prevents cleanup. No persistent workaround is installed. This comparison remains
untested; if firmware powers the controllers off independently, D3cold restriction
may not be sufficient. Do not restore usability by repeated blind PCI rescans.

The initial no-D3cold guard rejected the Wi-Fi adapter because its root-port
scope incorrectly included `00:1d.3`. No power settings were changed. Sysfs
ancestry confirms the Thunderbolt roots are `00:1c.4` (left, `03:00.0`) and
`00:1d.0` (right, `79:00.0`); Wi-Fi is under `00:1d.3` and is excluded. The script
now checks those ancestry relationships before any writes as well as device IDs.

## No-D3cold test result

The corrected runtime restriction test returned with Wi-Fi and Touch Bar working.
Noirq resume took 4.371 seconds, compared with 81.663 seconds in the preceding
unrestricted test. One comparison cannot establish reliable causality or stability.
Thunderbolt/bridge power-state errors persisted, both NHI functions remained in
D3cold afterward, and USB controllers `06:00.0` and `7c:00.0` disappeared again.
The log also shows a pending IRQ 9 wake before entry to suspend-to-idle and closely spaced monotonic idle-entry/exit messages. Monotonic timestamps
do not include time asleep, so their spacing alone cannot establish an immediate
wake; timed wake and sleep duration require wall-clock and user confirmation. The restriction reduced observed delay but did not preserve
the complete controller topology. It has not been made persistent. Reboot to
recover the missing controllers before another experiment. Future validation
must cover actual idle duration, controller preservation, USB-C peripheral use,
lid wake and repeated cycles, as well as Wi-Fi and Touch Bar operation.

## Staged Thunderbolt remove/rescan comparison

A separate one-shot comparison is now available:

```bash
# Save work, disconnect every USB-C/Thunderbolt peripheral, then reboot first.
sudo ./scripts/suspend-test s2idle-tb-cycle
```

This explicitly removes the two internal Thunderbolt subtrees (`03:00.0`,
`79:00.0`) before real s2idle and rescans their verified root ports after wake.
It implements the narrow controller-lifecycle approach reported in the independent
same-model runbook linked above, rather than copying that runbook's system-wide
installer. It is not yet tested on this host.

All known controller IDs/ancestry must match before mutation. Additional PCI
endpoints, block devices (mounted or unmounted) and ordinary USB peripherals under
those trees stop the test before removal or suspend. Keep only a charger connected.
Do not bypass a refusal. Wi-Fi (`02:00.0`), NVMe and the main T1 USB controller
are outside these trees and are not removed. Kernel hot-removal still executes
Thunderbolt/xHCI driver teardown; a driver fault can prevent completion. This is
an explicit foreground test, not an automatic sleep hook that cannot cancel sleep.

The 20-second RTC alarm is armed after subtree preparation. Cleanup rescans only
the two roots, twice, and checks that all expected functions and their NHI/xHCI
drivers reappear. Runtime overrides/alarm are removed. No persistent sleep policy,
module reload, network-profile edit or UKI rebuild is involved. A hang or failed
rescan may still require reboot. Success must include a real sleep interval,
prompt wake, controller/USB-C preservation, Wi-Fi and Touch Bar function, and
repeatable cycles. No result has yet established a permanent suspend solution.

## First successful controller-cycle result

The user ran the subtree-cycle test on a fresh boot. It returned status 0 with
no inaccessible/not-ready controller errors in the selected events. Noirq resume
completed in 233.135 ms. All 16 expected functions returned, including both NHI
and xHCI controllers bound to their expected drivers. The journal's wall-clock
suspend-entry/exit times span about 22 seconds, consistent with the 20-second
RTC alarm plus transition time. Functional Wi-Fi/Touch Bar/audio confirmation,
repeated cycles, lid wake, peripherals and battery drain remain pending. This
is one successful isolated test, not a permanent validated setup.

The test initially armed the RTC twice; the redundant earlier arm has been
removed, leaving one alarm after preparation. Closely spaced monotonic kernel
idle-entry/exit timestamps must not be treated as proof of immediate wake because
that clock does not count time asleep.

## Persistent configuration and lid testing

Three consecutive isolated subtree-cycle tests completed successfully. Each
restored all 16 PCI functions and expected NHI/xHCI drivers; noirq resume stayed
around 233–234 ms. The user confirmed all hardware after the first cycle, and
trackpad/Wi-Fi after the repeats. This supports persistence testing on the recorded
kernel, with peripheral-free suspend; it does not validate attached devices,
long sleep or battery drain.

Install from the reviewed checkout while all controllers are present:

```bash
sudo ./scripts/install-suspend
```

It checks the Touch Bar resume repair, exact topology/peripheral guards, current
boot hash and conflicting sleep policy. It refuses existing persistence files.
Root-owned helper, unit and policy are installed with an integrity record;
`check-upgrades` checks their integrity and enablement. Nothing is suspended or
reloaded during installation, and the UKI checksum is checked unchanged.

The configuration uses `MemorySleepMode=s2idle` and `SuspendState=mem` in
`/etc/systemd/sleep.conf.d/zz-macbookpro13-2.conf`. systemd reads this on each
suspend; the current `/sys/power/mem_sleep` can still show deep until the first
managed suspend. No kernel command-line or UKI change is needed.

`macbookpro13-2-suspend.service` is a **required, ordered dependency of
systemd-suspend.service**, not a system-sleep hook. Its preparation performs
all guards before removing anything. A failed preparation prevents that suspend
service from starting. After wake, StopWhenUnneeded and ExecStop restore both
trees. ExecStopPost also restores a partial preparation after failure, using a
private `/run` marker. The helper verifies controller IDs and driver bindings
before removing the marker. Preparation and restoration through this dependency were verified on the host.
It applies to normal systemd suspend only, not hibernation/hybrid sleep or direct
writes to `/sys/power/state`.

This initial policy refuses any attached USB peripheral, storage (even unmounted)
or unexpected PCI endpoint under the two Thunderbolt trees. Disconnect them
before closing the lid. It intentionally cannot support docked/storage suspend
yet. A refusal should leave the desktop awake; the screen may already be locked
by the desktop's sleep preparation. New hotplug events racing guard checks are
not proven safe: keep peripherals disconnected throughout suspend. An automatic
sleep hook whose failure cannot cancel sleep is not installed.

After installation, save work and first test an ordinary manual suspend with the
lid open and no peripherals:

```bash
systemctl suspend
```

Wake with a brief power-button press; inspect the service afterward:

```bash
journalctl -b -u macbookpro13-2-suspend.service --no-pager
sudo ./scripts/suspend-guard check
```

If restoration is still running, wait for that service's stop job to complete
before checking topology. Confirm Wi-Fi, Touch Bar, audio and the desktop, then
close/open the lid for a separate lid-wake test. A failed lid wake must not be
marked fixed merely because RTC wake succeeded. Repeat cycles, then measure
longer sleep and battery drain; s2idle can consume more power than deep S3.

Rollback of the exact installed files:

```bash
sudo ./scripts/disable-suspend
```

It verifies the installation manifest, refuses an active suspend, restores any
pending subtree operation, disables the dependency and removes only the recorded
helper/unit/policy. It does not touch boot files or unrelated settings. Modified
files require manual review. The previous deep-sleep failure remains after
rollback; do not interpret rollback as a working alternate sleep policy.
Installation records remain private in `/var/lib/macbookpro13-2-suspend-install-*`.
The persistence installer and real service dependency were verified on the host.
Lid wake failed despite the temporary EC wake experiment; no EC wake policy was
persisted. The Wi-Fi DKMS migration subsequently passed all installation checks.
