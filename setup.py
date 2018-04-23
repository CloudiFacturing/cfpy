from setuptools import setup

setup(name='cfpy',
      version='0.1',
      description='Library for accessing infrastructure services in CloudFlow and its derivatives',
      author='Robert Schittny',
      author_email='robert.schittny@sintef.no',
      packages=['cfpy'],
      install_requires=['requests', 'suds_jurko'],
      zip_safe=False)
