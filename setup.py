from setuptools import setup

setup(name='clfpy',
      version='0.8.0',
      description='Library for accessing infrastructure services in CloudFlow and its derivatives',
      url='https://github.com/CloudiFacturing/clfpy',
      author='Robert Schittny',
      author_email='robert.schittny@sintef.no',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
      ],
      packages=['clfpy'],
      install_requires=['requests', 'suds_jurko'],
      python_requires='>=2.7, <4',
)
