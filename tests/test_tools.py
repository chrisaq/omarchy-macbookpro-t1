import importlib.machinery
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('status', str(ROOT / 'scripts/hardware-status'))
spec = importlib.util.spec_from_loader(loader.name, loader)
status = importlib.util.module_from_spec(spec)
loader.exec_module(status)

class StatusTests(unittest.TestCase):
    def test_detected_is_not_verified(self):
        result = status.observation_status({'speakers': True}, {}, 'new')
        self.assertEqual(result['speakers']['status'], 'detected')
        self.assertEqual(result['microphone']['status'], 'untested')

    def test_kernel_change_invalidates_current_pass(self):
        tests = {'touchbar': [{'kernel': 'old', 'result': 'passed'}]}
        self.assertEqual(status.observation_status({'touchbar': True}, tests, 'new')['touchbar']['status'], 'previous-kernel-test')
        self.assertEqual(status.observation_status({}, tests, 'old')['touchbar']['status'], 'user-verified')

    def test_latest_failure_overrides_previous_pass(self):
        tests = {'speakers': [{'kernel': 'k', 'result': 'passed'}, {'kernel': 'k', 'result': 'failed'}]}
        self.assertEqual(status.observation_status({}, tests, 'k')['speakers']['status'], 'failed')

    def test_record_round_trip_preserves_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'results.json'
            for result in ('passed', 'failed'):
                subprocess.run([str(ROOT / 'scripts/record-test'), 'touchbar', result, '--notes', 'Explicit test observation', '--file', str(path)], check=True, capture_output=True)
            history = json.loads(path.read_text())['touchbar']
            self.assertEqual([v['result'] for v in history], ['passed', 'failed'])
            self.assertEqual(history[-1]['kernel'], platform.release())

class AudioPrebuildTests(unittest.TestCase):
    def test_false_success_download_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / 'install.cirrus.driver.sh'
            fake.write_text('#!/bin/sh\nexit 0\n')
            fake.chmod(0o755)
            result = subprocess.run([str(ROOT / 'scripts/audio-pre-build-checked.sh'), '7.2.5-test'], cwd=directory, capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_generated_source_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            fake = Path(directory) / 'install.cirrus.driver.sh'
            fake.write_text('#!/bin/sh\nmkdir -p build/hda/codecs/cirrus\ntouch build/hda/Makefile build/hda/codecs/cirrus/cs8409.c\n')
            fake.chmod(0o755)
            subprocess.run([str(ROOT / 'scripts/audio-pre-build-checked.sh'), '7.2.5-test'], cwd=directory, check=True)

class DocumentationTests(unittest.TestCase):
    def test_local_links_resolve(self):
        import re
        for document in ROOT.rglob('*.md'):
            if 'build' in document.relative_to(ROOT).parts:
                continue
            for link in re.findall(r'\]\(([^)]+)\)', document.read_text()):
                if '://' in link or link.startswith('#'):
                    continue
                target = link.split('#')[0]
                self.assertTrue((document.parent / target).exists(), f'{document}: {link}')

if __name__ == '__main__':
    unittest.main()
