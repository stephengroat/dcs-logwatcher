#!/usr/bin/env python

from distutils.core import setup

setup(name='dcs-logwatcher',
      version='0.1',
      description='DCS Logwatcher',
      author='Stephen Groat',
      author_email='stephen@egroat.com',
      scripts=['scripts/dcs-logwatcher'],
      py_modules=['logwatcher.QLock', 'logwatcher.LogDirectory'],
     )
