import os as _os


def yuv420p():
    info = {
        'path': _os.path.join(__path__[0], 'cockatoo_yuv420p.mp4'),
        'shape': (360, 640),
        'fps': 20
    }
    return info


def yuv444():
    info = {
        'path': _os.path.join(__path__[0], 'cockatoo.mp4'),
        'shape': (720, 1280),
        'fps': 20
    }
    return info
