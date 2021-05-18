import subprocess
import shlex
import json
from sys import platform

__all__ = ['get_bin', 'detect_gpu_coarse', 'ffprobe_metadata']


def get_bin():
    if platform == "linux" or platform == "linux2":
        ffmpeg_bin = "ffmpeg"
    elif platform == "darwin":
        raise NotImplemented
    elif platform == "win32":
        ffmpeg_bin = "ffmpeg.exe"
    return ffmpeg_bin


def detect_gpu_coarse():
    try:
        subprocess.check_output('nvidia-smi')
        print('Nvidia GPU detected!')
        return True
    except Exception:  # this command not being found can raise quite a few different errors depending on the configuration
        print('No Nvidia GPU in system!')
        return False


def ffprobe_metadata(src):
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(src)
    # run the ffprobe process, decode stdout into utf-8 & convert to JSON
    ffprobeOutput = subprocess.check_output(args).decode('utf-8')
    ffprobeOutput = json.loads(ffprobeOutput)

    return ffprobeOutput
