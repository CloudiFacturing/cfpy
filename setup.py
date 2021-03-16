import setuptools

setuptools.setup(name='clfpy',
      version='1.3.2',
      description='Library for accessing infrastructure services in SemWES and its derivatives',
      url='https://github.com/CloudiFacturing/clfpy',
      author='Robert Schittny',
      author_email='robert.schittny@sintef.no',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
      ],
      packages=setuptools.find_packages(),
      install_requires=['requests', 'suds_jurko', 'future', 'future_fstrings'],
      python_requires='>=2.7, <4',
      scripts=['clfpy/cli/clfpy_cli']
)
