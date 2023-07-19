from setuptools import setup, find_packages

setup(
    name='exwrtc',
    version='1.0.0',
    packages=find_packages(),
    python_requires='>=3.0',
    author='Azeranth',
    author_email='jdgeci@gmail.com',
    description='Portable Data Exfiltration over wRTC',
    long_description='A server and client implementation for handling structured messages for C2 and file transfer over wRTC',
    url='www.github.com/Azeranth/exwrtc',
    license='GPLv3.0'
)