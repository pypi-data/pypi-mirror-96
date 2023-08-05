#!/usr/bin/env python3
import sys
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

if sys.version_info < (3,4):
    sys.exit("Python 3.4+ is required; you are using %s" % sys.version)

setup(name="aztec_code_generator",
      version="0.8",
      description='Aztec Code generator in Python',
      long_description=open('description.rst').read(),
      author='Dmitry Alimov',
      author_email="dvalimov@gmail.com",
      install_requires=open('requirements.txt').readlines(),
      extras_require={
          "Image": [
              "pillow>=3.0,<6.0; python_version < '3.5'",
              "pillow>=3.0,<8.0; python_version >= '3.5' and python_version < '3.6'",
              "pillow>=8.0; python_version >= '3.6'",
          ]
      },
      tests_require=open('requirements-test.txt').readlines(),
      license='MIT',
      url="https://github.com/dlenski/aztec_code_generator",
      py_modules=["aztec_code_generator"],
      )
