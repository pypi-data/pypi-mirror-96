#!/usr/bin/env python

from distutils.core import setup
import setuptools

setup(name='Voicelab',
      version='0.2-beta.0',
      description='Python GUI for working with voicefiles',
      author='David Feinberg',
      author_email='feinberg@mcmaster.ca',
      packages=['Voicelab'],
      install_requires=[
            'qdarkstyle',
            'praat-parselmouth==0.4.0',
            'librosa',
            'openpyxl',
            'PyQt5',
            'seaborn',
      ]
     )
