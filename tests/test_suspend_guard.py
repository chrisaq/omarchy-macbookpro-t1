import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader('guard', str(Path(__file__).resolve().parents[1] / 'scripts/suspend-guard'))
spec = importlib.util.spec_from_loader(loader.name, loader)
guard = importlib.util.module_from_spec(spec)
loader.exec_module(guard)

class GuardTests(unittest.TestCase):
    def fixture(self, folder):
        root = Path(folder)
        pci = root / 'pci'
        pci.mkdir()
        for address, device in guard.SPECS.items():
            if address in guard.ROOTS:
                physical = root / 'physical' / address
            else:
                port = '0000:00:1c.4' if address.split(':')[1] in ('03', '04', '05', '06') else '0000:00:1d.0'
                tree = '0000:03:00.0' if port.endswith('1c.4') else '0000:79:00.0'
                physical = root / 'physical' / port / tree
                if address != tree:
                    physical = physical / address
            physical.mkdir(parents=True, exist_ok=True)
            (physical / 'vendor').write_text('0x8086\n')
            (physical / 'device').write_text('0x' + device + '\n')
            (physical / 'remove').write_text('')
            (pci / address).symlink_to(physical, target_is_directory=True)
        for name in ('block', 'usb'):
            (root / name).mkdir()
        return root, pci

    def run_check(self, root, pci):
        real_path = Path
        def mapped(path):
            return {'/sys/class/block': root / 'block', '/sys/bus/usb/devices': root / 'usb'}.get(str(path), real_path(path))
        with patch.object(guard, 'PCI', pci), patch.object(guard, 'Path', side_effect=mapped):
            guard.check()

    def test_bare_machine_allowed_and_wifi_root_excluded(self):
        with tempfile.TemporaryDirectory() as folder:
            root, pci = self.fixture(folder)
            wifi = root / 'physical/0000:00:1d.3/0000:02:00.0'
            wifi.mkdir(parents=True)
            (pci / '0000:02:00.0').symlink_to(wifi)
            self.run_check(root, pci)

    def test_external_pci_endpoint_blocks_sleep(self):
        with tempfile.TemporaryDirectory() as folder:
            root, pci = self.fixture(folder)
            extra = (pci / guard.TREES[0]).resolve() / 'external'
            extra.mkdir()
            (pci / '0000:08:00.0').symlink_to(extra)
            with self.assertRaises(RuntimeError):
                self.run_check(root, pci)

    def test_storage_and_usb_block_sleep_even_without_mounts(self):
        for category, name in (('block', 'sda'), ('usb', '9-1'), ('usb', '9-1.2:1.0')):
            with self.subTest(category=category), tempfile.TemporaryDirectory() as folder:
                root, pci = self.fixture(folder)
                target = (pci / guard.TREES[0]).resolve() / 'peripheral'
                target.mkdir()
                (root / category / name).symlink_to(target)
                with self.assertRaises(RuntimeError):
                    self.run_check(root, pci)

    def test_missing_or_wrong_controller_blocks_sleep(self):
        with tempfile.TemporaryDirectory() as folder:
            root, pci = self.fixture(folder)
            (pci / '0000:06:00.0' / 'device').write_text('0xffff')
            with self.assertRaises(RuntimeError):
                self.run_check(root, pci)

    def test_failed_partial_removal_keeps_restore_marker(self):
        with tempfile.TemporaryDirectory() as folder:
            root, pci = self.fixture(folder)
            marker = root / 'run/pending'
            with patch.object(guard, 'PCI', pci), patch.object(guard, 'MARKER', marker), patch.object(guard, 'check'):
                with self.assertRaises(RuntimeError):
                    guard.prepare()  # Regular fixture remove files cannot hot-remove.
                self.assertTrue(marker.exists())

    def test_unit_requires_preparation_and_cleans_failed_start(self):
        root = Path(__file__).resolve().parents[1]
        unit = (root / 'systemd/macbookpro13-2-suspend.service').read_text()
        self.assertIn('RequiredBy=systemd-suspend.service', unit)
        self.assertIn('Before=systemd-suspend.service', unit)
        self.assertIn('ExecStopPost=/usr/local/lib/macbookpro13-2-omarchy/suspend-guard restore', unit)
        self.assertNotIn('ConditionPath', unit)  # A skipped guard must not permit sleep.
