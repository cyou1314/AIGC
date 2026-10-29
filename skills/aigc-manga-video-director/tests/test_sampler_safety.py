import csv
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
HAS_MEDIA_DEPS = importlib.util.find_spec("PIL") is not None and importlib.util.find_spec("numpy") is not None
if HAS_MEDIA_DEPS:
    spec = importlib.util.spec_from_file_location("fast_sampler_test", SCRIPTS / "fast_sample_video.py")
    fast = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fast)
else:
    fast = None

@unittest.skipUnless(HAS_MEDIA_DEPS, "Pillow and NumPy are needed for sampler checks")
class SamplerSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'input.mp4'
        self.source.write_bytes(b'source video placeholder')
        self.existing = self.root / 'existing'
        self.existing.mkdir()
        self.marker = self.existing / 'keep.txt'
        self.marker.write_text('do not replace')
        self.stub = self.root / 'stubs'
        self.stub.mkdir()
        (self.stub / 'cv2.py').write_text('')
        self.ffmpeg = self.root / 'ffmpeg-stub'
        self.ffmpeg.write_text('unused')

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, script, source):
        env = dict(os.environ, PYTHONPATH=str(self.stub), AIGC_FFMPEG=str(self.ffmpeg))
        return subprocess.run([sys.executable, str(SCRIPTS / script), str(source), '--out', str(self.existing)], env=env, capture_output=True, text=True)

    def test_existing_output_folder_is_never_reused(self):
        image = self.root / 'source.png'
        image.write_bytes(b'placeholder')
        for name, source in [('fast_sample_video.py', self.source), ('smart_sample_video.py', self.source), ('shot_pipeline.py', self.source), ('enhance_sketch_frames.py', image)]:
            with self.subTest(script=name):
                result = self.invoke(name, source)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Output folder already exists', result.stderr)
                self.assertEqual(self.marker.read_text(), 'do not replace')
                self.assertEqual(self.source.read_bytes(), b'source video placeholder')

    def test_scene_time_is_unknown_and_fixed_retained_indices_are_not_renumbered(self):
        frames = [self.root / 'frame_00001.jpg', self.root / 'frame_00009.jpg']
        manifest = self.root / 'manifest.csv'
        fast.write_manifest(frames, manifest, 0.5, 'scene')
        with manifest.open(encoding='utf-8') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([r['timestamp_hint'] for r in rows], ['', ''])
        fast.write_manifest(frames, manifest, 0.5, 'fixed')
        with manifest.open(encoding='utf-8') as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([r['timestamp_hint'] for r in rows], ['00:00.00', '00:16.00'])

    def test_max_frames_one_is_valid(self):
        frames = [self.root / f'frame_{i:05d}.jpg' for i in range(1,4)]
        for frame in frames: frame.write_bytes(b'x')
        self.assertEqual(fast.trim_frames(frames, 1), [frames[0]])
        self.assertTrue(frames[0].exists())

if __name__ == '__main__':
    unittest.main()
