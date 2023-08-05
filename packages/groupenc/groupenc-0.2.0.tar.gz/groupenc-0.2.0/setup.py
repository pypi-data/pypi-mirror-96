"""
groupenc: Group Encryption Utilities
"""
from setuptools import setup, find_packages

VERSION = '0.2.0'

def get_requirements():
    with open('requirements.txt') as requirements:
        for req in requirements:
            req = req.strip()
            if req and not req.startswith('#'):
                yield req

def get_readme():
    with open('README.md') as readme:
        return readme.read()

setup(name='groupenc',
      version=VERSION,
      description="groupenc: Group Encryption Utilities",
      long_description=get_readme(),
      long_description_content_type='text/markdown',
      classifiers=
      [
          'Topic :: Software Development :: Libraries',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
      ],
      keywords='groupenc encryption group vault offline',
      author='Karthik Kumar Viswanathan',
      author_email='karthikkumar@gmail.com',
      url='http://github.com/guilt/groupenc',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=list(get_requirements()),
     )
