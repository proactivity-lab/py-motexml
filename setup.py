"""
motexml: MoteXML binary XML encoding format python support package.
Warpper around shared library for python.
"""

from setuptools import setup
from os.path import join as pjoin

import motexml

doclines = __doc__.split("\n")

setup(name='motexml',
      version=motexml.version,
      description='MoteXML binary XML encoding format python support package.',
      long_description='\n'.join(doclines[2:]),
      url='http://github.com/proactivity-lab/py-motexml',
      author='Raido Pahtma',
      author_email='raido.pahtma@ttu.ee',
      license='MIT',
      platforms=['any'],
      packages=['motexml'],
      install_requires=["argparse"],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=[pjoin('bin', 'motexml-generate'), pjoin('bin', 'motexml-to-xml'), pjoin('bin', 'motexml-from-xml')],
      zip_safe=False)
