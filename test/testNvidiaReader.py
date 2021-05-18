import unittest
import imageio
import numpy as np

from pynviread import NvidiaReader
import pynviread.examples as ex


class TestFramework(unittest.TestCase):
    def load_yuv420p(self):
        reader = imageio.get_reader(ex.yuv420p()['path'])
        frames = []
        for i, im in enumerate(reader):
            frames.append(im)
            if i > 8:
                break
        frames = np.stack(frames)
        return frames

    def testReader_yuv420p(self):
        yuv420 = self.load_yuv420p()
        with NvidiaReader(src=ex.yuv420p()['path'], verbose=True) as reader:
            video = reader.read()
            difference = np.abs(video[:10].astype('float') - yuv420.astype('float')).mean()
            self.assertTrue(difference < 1, f'Readed video doesnt match imageio ground-truth')

    def testGenReader_yuv420p(self):
        yuv420 = self.load_yuv420p()
        with NvidiaReader(src=ex.yuv420p()['path'],
                          input_options=['-hide_banner', '-loglevel', 'error']) as reader:
            video = np.stack([frame for frame in reader])
            difference = np.abs(video[:10].astype('float') - yuv420.astype('float')).mean()
            self.assertTrue(difference < 1, f'Readed video doesnt match imageio ground-truth')

    def testFileExist(self):
        with self.assertRaises(AssertionError):
            reader = NvidiaReader(src='./cacatua.mp4', verbose=True)

    def testPixelFormatError(self):
        with self.assertRaises(AssertionError):
            reader = NvidiaReader(src=ex.yuv444()['path'], verbose=True)
