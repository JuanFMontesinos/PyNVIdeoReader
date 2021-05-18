import subprocess as sp
from warnings import warn
from typing import Tuple
import os

import numpy as np

from .subprocess_calls import *

FFMPEG_BIN = get_bin()

DEFAULT_GPU_CODEC = 'h264_cuvid'
DEFAULT_CPU_CODEC = 'h264'
EXPECTED_CODECS = ['h264', 'h265']
EXPECTED_PIX_FMT = ['yuv420p']
MISC_METADATA = {'time_base': {'name': 'time_base', 'type': str},
                 'duration': {'name': 'duration', 'type': float},
                 'avg_frame_rate': {'name': 'framerate', 'type': str}
                 }


class NvidiaReader:
    """
    FFMPEG wrapper that enables video decoding through nvidia GPU.
    Calls ffmpeg as follows
    ffmpeg [input options] -i input [output options] output

    Note that ffprobe is used to infer image shape and other metadata. If you
    crop, rescale or change the color space you have to manually pass output metadata for the buffer to work properly.


    :param src: Path to the video
    :param img_shape: (tuple) Image shape (heigth,width)
    :param verbose: (bool)
    :param input_options: (list) additional commands to pass to ffmpeg
    :param output_options: (list) additional commands to pass to ffmpeg
    """

    def __init__(self, src: str, img_shape: Tuple[int, int] = None, verbose: bool = False,
                 input_options=list(), output_options=list()):
        assert os.path.exists(src), f'File {src} doesnt exist'

        # PRIVATE attr
        self._pipe = None

        self._verbose = verbose
        self._init_colorspace()

        # INPUT attr
        self.src = src
        self.img_shape = img_shape

        self._analyze_video(src)

        self.n_elements = self.img_shape[0] * self.img_shape[1] * self.n_channel

        self._args = [FFMPEG_BIN,
                      '-vcodec', self._set_codec()] + \
                     input_options + \
                     ['-i', src, ] + \
                     output_options + \
                     ['-f', 'image2pipe',
                      '-pix_fmt', 'rgb24',
                      '-vcodec', 'rawvideo',
                      '-']

    def _analyze_video(self, path):
        try:
            info = ffprobe_metadata(path)['streams'][0]
        except Exception as ex:
            print('Automatic video analysis failed')
            if self.img_shape is None:
                raise ValueError(f'img_shape is required when auto-analysis fails. Please, rerun providing that data.')
        self._define_shape(info)
        self._check_codec(info)
        self._check_pix_fmt(info)
        self._set_irrelevant_metadata(info)

    def _define_shape(self, info):
        metadata_shape = (info['height'], info['width'])
        if self.img_shape is None:
            self.img_shape = metadata_shape
        else:
            if metadata_shape != self.img_shape:
                warn(f'Shape read in metadata is {metadata_shape} meanwhile shape'
                     f'provided by the user is {self.img_shape}. '
                     f'Mismatching may indicate errors.')

    @staticmethod
    def _check_codec(info):
        codec = info['codec_name']
        assert codec in EXPECTED_CODECS, f'Video codec must be {" ".join(EXPECTED_CODECS)} but {codec} found'

    @staticmethod
    def _check_pix_fmt(info):
        fmt = info['pix_fmt']
        assert fmt in EXPECTED_PIX_FMT, f'Video codec must be {" ".join(EXPECTED_PIX_FMT)} but {fmt} found'

    def _set_irrelevant_metadata(self, info):
        for attr in MISC_METADATA:
            value = info.get(attr)
            if value is not None:
                value = MISC_METADATA[attr]['type'](value)
            setattr(self, MISC_METADATA[attr]['name'], value)
        self.raw_metadata = info

    def _init_colorspace(self):
        self.color_space = 'rgb'
        self.n_channel = 3

    def _set_codec(self):
        if detect_gpu_coarse():
            return DEFAULT_GPU_CODEC
        else:
            return DEFAULT_CPU_CODEC

    def _pipe_call(self):
        self._pipe = sp.Popen(self._args, stdout=sp.PIPE, bufsize=10 ** 8)
        return self

    def _pipe_as_generator(self):
        while True:
            bytes = self._pipe.stdout.read(self.n_elements)
            if bytes != b'':
                image = np.frombuffer(bytes, dtype='uint8')
                yield image.reshape(self.img_shape + (self.n_channel,))
            else:
                break

    def __enter__(self):
        self._pipe_call()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pipe.stdout.flush()

    def __iter__(self):
        yield from self._pipe_as_generator()

    @property
    def img_shape(self):
        return self._imgshape

    @img_shape.setter
    def img_shape(self, shape):
        if shape is not None:
            assert isinstance(shape, tuple), f'image_shape must be a {tuple} but {type(shape)} found'
            assert len(shape) == 2, f'img_shape must be (H,w)'
        self._imgshape = shape

    def read(self):
        """
        Read the whole video at once.
        Be aware max. buffer size is 10**8
        :return: np.ndarray of shape (T,H,W,3)
        """
        bytes = self._pipe.stdout.read()
        array = np.frombuffer(bytes, dtype='uint8')
        nframes = int(array.shape[0] / (self.img_shape[0] * self.img_shape[1] * self.n_channel))
        video = array.reshape((nframes,) + self.img_shape + (self.n_channel,))
        return video
