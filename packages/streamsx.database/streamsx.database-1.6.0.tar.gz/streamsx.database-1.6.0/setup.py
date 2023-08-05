from setuptools import setup
import streamsx.database
setup(
  name = 'streamsx.database',
  packages = ['streamsx.database'],
  include_package_data=True,
  version = streamsx.database.__version__,
  description = 'Database integration for IBM Streams',
  long_description = open('DESC.txt').read(),
  author = 'IBM Streams @ github.com',
  author_email = 'hegermar@de.ibm.com',
  license='Apache License - Version 2.0',
  url = 'https://github.com/IBMStreams/streamsx.database',
  keywords = ['streams', 'ibmstreams', 'streaming', 'analytics', 'streaming-analytics', 'db2', 'database'],
  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
  install_requires=['streamsx>=1.14.6', 'streamsx.toolkits'],
  
  test_suite='nose.collector',
  tests_require=['nose']
)
