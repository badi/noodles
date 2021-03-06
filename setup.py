from setuptools import setup, find_packages
import os
import textwrap


# IMPORTANT use semantic versioning
# http://semver.org/
VERSION = '0.5.1'


module_dir = 'noodles'
version_file = os.path.join(module_dir, 'version.py')

version_module = textwrap.dedent("""\
# WARNING
# This file is autogenerated
# Do not modify by hand

version = '{}'
""".format(VERSION))


with open(version_file, 'w') as fd:
    fd.write(version_module)


setup(name='noodles',
      version=VERSION,
      description='Analyze Python program dependencies',
      author="Badi' Abdul-Wahid",
      author_email='abdulwahidc@gmail.com',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'noodles = noodles.main:main'
          ]
      }
      )
