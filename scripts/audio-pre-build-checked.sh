#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
[[ $# -eq 1 ]] || { echo 'Expected target kernel release.' >&2; exit 2; }
./install.cirrus.driver.sh -k "$1" --dkms
# Upstream can return success after both kernel-source downloads fail.
# Reject that before compilation and give DKMS a nonzero pre-build result.
[[ -f build/hda/Makefile && -f build/hda/codecs/cirrus/cs8409.c ]] || {
    echo 'Audio pre-build did not produce the expected kernel source.' >&2
    exit 1
}
