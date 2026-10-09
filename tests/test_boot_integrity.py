import hashlib
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

path = Path(__file__).resolve().parents[1] / 'scripts/boot-integrity'
loader = importlib.machinery.SourceFileLoader('boot_integrity', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)

class BootIntegrityTests(unittest.TestCase):
    def fixture(self, folder, suffix):
        root = Path(folder)
        image = root / module.IMAGE
        image.parent.mkdir(parents=True)
        image.write_bytes(b'test UKI')
        (root / 'limine.conf').write_text('  path: boot():/' + module.IMAGE + suffix + '\n')
        return root

    def test_correct_blake2_hash_and_read_only(self):
        with tempfile.TemporaryDirectory() as work:
            digest = hashlib.blake2b(b'test UKI').hexdigest()
            root = self.fixture(work, '#' + digest)
            before = (root / 'limine.conf').read_bytes()
            self.assertTrue(module.inspect(root))
            self.assertEqual(before, (root / 'limine.conf').read_bytes())
            self.assertEqual(b'test UKI', (root / module.IMAGE).read_bytes())

    def test_missing_malformed_sha512_or_stale_hash(self):
        for suffix in ('', '#bad', '#' + hashlib.sha512(b'test UKI').hexdigest(), '#' + '0' * 128):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as work:
                self.assertFalse(module.inspect(self.fixture(work, suffix)))

    def test_conflicting_duplicate_is_not_ignored(self):
        with tempfile.TemporaryDirectory() as work:
            root = self.fixture(work, '#' + hashlib.blake2b(b'test UKI').hexdigest())
            with (root / 'limine.conf').open('a') as stream:
                stream.write('path: boot():/' + module.IMAGE + '#' + '0' * 128 + '\n')
            self.assertFalse(module.inspect(root))

    def test_unrelated_entry_is_not_assumed_to_be_target(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            (root / 'limine.conf').write_text('path: boot():/other.efi#hash\n')
            with self.assertRaises(RuntimeError):
                module.inspect(root)

    def test_repair_rejects_fixture_before_modification(self):
        with tempfile.TemporaryDirectory() as work:
            with self.assertRaises(RuntimeError):
                module.repair(Path(work))
