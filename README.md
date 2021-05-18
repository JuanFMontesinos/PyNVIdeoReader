# Python Nvidia Video Reader

GPU Accelerated video decoder.  
Read your .mp4 videos with and Nvidia GPU.

This is a wrapper around NVIDIA VIDEO CODEC SDK and FFMPEG.

## Supported formats and hardware

You can find extended documentation
in [Nvidia site](https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/index.html)

![](https://developer.nvidia.com/sites/default/files/akamai/designworks/images-videocodec/VCSDK_007a.png)

Check if your GPU is
suitable [here](https://developer.nvidia.com/video-encode-and-decode-gpu-support-matrix-new#Encoder)

Roughly 10XX Generation supports h264 and 30XX gen supports h264,h265 and av1.

CURRENTLY ONLY **H264** IS SUPPORTED  
*Tested in linux for RTX 3090*

## Quick start

Be sure you have ffmpeg with nvidia codecs:  
`ffmpeg -codecs | grep cuvid`  
You should see something like, look for cuvid:

```
 DEV.LS h264                 H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (decoders: h264 h264_crystalhd h264_v4l2m2m h264_vdpau h264_cuvid ) (encoders: libx264 libx264rgb h264_nvenc h264_omx h264_v4l2m2m h264_vaapi nvenc nvenc_h264 )
 DEV.L. hevc                 H.265 / HEVC (High Efficiency Video Coding) (decoders: hevc hevc_cuvid ) (encoders: libx265 nvenc_hevc hevc_nvenc hevc_vaapi )
 DEVIL. mjpeg                Motion JPEG (decoders: mjpeg mjpeg_cuvid ) (encoders: mjpeg mjpeg_vaapi )
 DEV.L. mpeg1video           MPEG-1 video (decoders: mpeg1video mpeg1video_vdpau mpeg1_v4l2m2m mpeg1_cuvid )
 DEV.L. mpeg2video           MPEG-2 video (decoders: mpeg2video mpegvideo mpegvideo_vdpau mpeg2_crystalhd mpeg2_v4l2m2m mpeg2_cuvid ) (encoders: mpeg2video mpeg2_vaapi )
 DEV.L. mpeg4                MPEG-4 part 2 (decoders: mpeg4 mpeg4_crystalhd mpeg4_v4l2m2m mpeg4_vdpau mpeg4_cuvid ) (encoders: mpeg4 libxvid mpeg4_v4l2m2m )
 D.V.L. vc1                  SMPTE VC-1 (decoders: vc1 vc1_crystalhd vc1_vdpau vc1_v4l2m2m vc1_cuvid )
 DEV.L. vp8                  On2 VP8 (decoders: vp8 vp8_v4l2m2m libvpx vp8_cuvid ) (encoders: libvpx vp8_v4l2m2m vp8_vaapi )
 DEV.L. vp9                  Google VP9 (decoders: vp9 vp9_v4l2m2m libvpx-vp9 vp9_cuvid ) (encoders: libvpx-vp9 vp9_vaapi )
```

Then pip-install the package  
`pip install pynvideo-reader`

## Examples
### Data loading
#### Loading frame-wise  (generator)

```
from pynviread import NvidiaReader
import pynviread.examples as ex
with NvidiaReader(src=ex.yuv420p()['path'], verbose=True) as reader:
    video = np.stack([frame for frame in reader]) #Loading as a generator
```

#### Loading whole-video

```
from pynviread import NvidiaReader
import pynviread.examples as ex
with NvidiaReader(src=ex.yuv420p()['path'], verbose=True) as reader:
    video = reader.read()
```

Custom ffmpeg commands can be passed to reshape, crop, resample... Note that `ffprobe` is used to infer image shape,
colorspace... Change the img_shape and number of channels accordingly.
### Custom ffmpeg calls
#### FFmpeg less verbose

```
from pynviread import NvidiaReader
import pynviread.examples as ex
with NvidiaReader(src=ex.yuv420p()['path'], verbose=True,
                  input_options=['-hide_banner','-loglevel','error']) as reader:
    video = reader.read()
```

#### Frame seeking  and cutting

This is not straight-forward, check [ffmpeg explanation](https://trac.ffmpeg.org/wiki/Seeking)

```
from pynviread import NvidiaReader
import pynviread.examples as ex
with NvidiaReader(src=ex.yuv420p()['path'], verbose=True,
                  input_options=['-ss','00:0:10'],
                  output_options=['-to','00:0:20']) as reader:
    video = reader.read()
```
In short, you can add as many commands as you want.  



