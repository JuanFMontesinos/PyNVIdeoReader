from setuptools import setup, find_packages
import re

VERSIONFILE = "pynviread/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(name='pynviread',
      version=verstr,
      description='GPU Accelerated video decoder using FFMPEG ',
      url='https://github.com/JuanFMontesinos/PyNVIdeoReader',
      author='Juan Montesinos',
      author_email='jfmontgar@gmail.com',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['numpy'],
      classifiers=[
          "Programming Language :: Python :: 3", ],
      zip_safe=False)
