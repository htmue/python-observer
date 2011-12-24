# -*- coding:utf-8 -*-
# Created by Hans-Thomas on 2011-12-11.
#=============================================================================
#   setup.py --- Install script
#=============================================================================
from distutils.core import setup


setup(
    name='observer',
    version='0.1.0',
    description='Directory/file change observer',
    author='Hans-Thomas Mueller',
    author_email='htmue@mac.com',
    url='https://github.com/htmue/python-observer',
    packages=['observer'],
    scripts=['bin/autorestart'],
)

#.............................................................................
#   setup.py
