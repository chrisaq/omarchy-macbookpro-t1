import argparse
from contextlib import ExitStack, nullcontext
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('wifi_tools', str(ROOT / 'scripts/wifi'))
spec = importlib.util.spec_from_loader(loader.name, loader)
wifi = importlib.util.module_from_spec(spec)
loader.exec_module(wifi)
TEMPLATE = b'sromrev=11\nmacaddr=xx:xx:xx:xx:xx:xx\nccode=00\nregrev=245\n'
MAC = '10:11:12:13:14:15'

class WiFiTests(unittest.TestCase):
    def fixture(self, folder, stack):
        root = Path(folder)
        target = root / 'firmware' / wifi.NAME
        target.parent.mkdir()
        state = root / 'state'
        for key, value in {'TEMPLATE_SHA256': wifi.sha(TEMPLATE), 'TARGET': target,
                           'STATE': state, 'RECORD': state / 'installed.json',
                           'DROPIN': root / 'wifi.conf'}.items():
            stack.enter_context(patch.object(wifi, key, value))
        for name in ('require_hardware', 'boot_check', 'deploy_helpers'):
            stack.enter_context(patch.object(wifi, name))
        stack.enter_context(patch.object(wifi, 'lock', side_effect=nullcontext))
        stack.enter_context(patch.object(wifi, 'inspect_initramfs', return_value=False))
        return target, wifi.personalize(TEMPLATE, MAC)

    def test_only_mac_is_changed(self):
        with patch.object(wifi, 'TEMPLATE_SHA256', wifi.sha(TEMPLATE)):
            data = wifi.personalize(TEMPLATE, MAC.upper())
            self.assertEqual(data, TEMPLATE.replace(wifi.PLACEHOLDER, b'macaddr=' + MAC.encode()))
            self.assertEqual(wifi.validate_candidate(data), wifi.sha(data))
            with self.assertRaises(RuntimeError):
                wifi.validate_candidate(data.replace(b'ccode=00', b'ccode=US'))

    def test_changed_or_duplicate_template_is_rejected(self):
        for data in (TEMPLATE + b'changed', TEMPLATE + wifi.PLACEHOLDER + b'\n'):
            with self.assertRaises(RuntimeError):
                wifi.personalize(data, MAC)

    def test_invalid_mac_is_rejected(self):
        for mac in ('xx:xx:xx:xx:xx:xx', '00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff',
                    '01:11:12:13:14:15', '00:90:4c:11:12:13', '10:11:12:13:14'):
            with self.subTest(mac=mac), self.assertRaises(RuntimeError):
                wifi.validate_mac(mac)

    def test_prepare_private_file_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(wifi, 'TEMPLATE_SHA256', wifi.sha(TEMPLATE)), patch.object(wifi.os, 'geteuid', return_value=1000):
            source = Path(folder) / 'template'
            source.write_bytes(TEMPLATE)
            output = Path(folder) / 'private/candidate'
            args = argparse.Namespace(mac=MAC, source=source, output=output)
            wifi.prepare(args)
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                wifi.prepare(args)

    def test_install_check_modified_file_and_guarded_rollback(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            target, data = self.fixture(folder, stack)
            candidate = Path(folder) / 'candidate'
            candidate.write_bytes(data)
            wifi.install(argparse.Namespace(command='install', candidate=candidate))
            self.assertEqual(target.read_bytes(), data)
            wifi.check(argparse.Namespace(boot=True, if_installed=False))
            target.write_bytes(data + b'changed')
            with self.assertRaises(RuntimeError):
                wifi.check(argparse.Namespace(boot=False, if_installed=False))
            with self.assertRaises(RuntimeError):
                wifi.rollback(argparse.Namespace())
            self.assertTrue(target.exists())
            target.write_bytes(data)
            wifi.rollback(argparse.Namespace())
            self.assertFalse(target.exists())
            self.assertFalse(wifi.RECORD.exists())
            self.assertTrue((wifi.STATE / 'candidate.txt').exists())

    def test_existing_generic_or_compressed_override_is_preserved(self):
        for name in ('brcmfmac43602-pcie.txt', wifi.NAME + '.zst'):
            with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
                target, data = self.fixture(folder, stack)
                candidate = Path(folder) / 'candidate'
                candidate.write_bytes(data)
                existing = target.parent / name
                existing.write_bytes(b'existing override')
                with self.assertRaises(RuntimeError):
                    wifi.install(argparse.Namespace(command='install', candidate=candidate))
                self.assertEqual(existing.read_bytes(), b'existing override')
                self.assertFalse(wifi.RECORD.exists())

    def test_adoption_does_not_rewrite_existing_candidate(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            target, data = self.fixture(folder, stack)
            target.write_bytes(data)
            timestamp = target.stat().st_mtime_ns
            wifi.install(argparse.Namespace(command='adopt'))
            self.assertEqual(target.stat().st_mtime_ns, timestamp)
            self.assertTrue(json.loads(wifi.RECORD.read_text())['adopted'])

    def test_early_wifi_installs_dropin_and_uses_supported_rebuild(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            target, data = self.fixture(folder, stack)
            stack.enter_context(patch.object(wifi, 'inspect_initramfs', return_value=True))
            rebuild = stack.enter_context(patch.object(wifi.subprocess, 'run'))
            candidate = Path(folder) / 'candidate'
            candidate.write_bytes(data)
            wifi.install(argparse.Namespace(command='install', candidate=candidate))
            self.assertEqual(wifi.DROPIN.read_bytes(), wifi.DROPIN_DATA)
            self.assertEqual(rebuild.call_args.args[0], [str(wifi.ROOT / 'boot-integrity'), '--repair'])
            wifi.rollback(argparse.Namespace())
            self.assertFalse(wifi.DROPIN.exists())

    def test_failed_rebuild_leaves_record_and_candidate_for_recovery(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            target, data = self.fixture(folder, stack)
            stack.enter_context(patch.object(wifi, 'inspect_initramfs', return_value=True))
            stack.enter_context(patch.object(wifi.subprocess, 'run', side_effect=wifi.subprocess.CalledProcessError(1, 'rebuild')))
            candidate = Path(folder) / 'candidate'
            candidate.write_bytes(data)
            with self.assertRaises(wifi.subprocess.CalledProcessError):
                wifi.install(argparse.Namespace(command='install', candidate=candidate))
            self.assertEqual(target.read_bytes(), data)
            self.assertTrue(wifi.RECORD.exists())

    def test_missing_unmanaged_record_is_not_a_pass_without_opt_in(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            self.fixture(folder, stack)
            with self.assertRaises(RuntimeError):
                wifi.check(argparse.Namespace(boot=False, if_installed=False))
            wifi.check(argparse.Namespace(boot=True, if_installed=True))
