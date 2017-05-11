import os, sys

from when import __version__

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()

SETUP_ARGS = dict(
    name='wrench',
    version=__version__,
    description=('Collection of random python tools and utilities '),
    long_description=long_description,
    url='https://github.com/cltrudeau/wrench',
    author='Christopher Trudeau',
    author_email='ctrudeau+pypi@arsensa.com',
    license='MIT',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='tools',
    test_suite='load_tests.get_suite',
    py_modules = ['when',],
    install_requires=[],
    tests_require=[
        'waelstow==0.10.0',
    ],
)

if __name__ == '__main__':
    from setuptools import setup
    setup(**SETUP_ARGS)
