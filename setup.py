import os, sys

VERSION='0.4.0'

install_requires = [
    'six>=1.9',
    'portalocker>=0.5.4',
]

if sys.version_info[:2] < (3,4):
    install_requires.append('enum34>=1.0.4')


readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()


SETUP_ARGS = dict(
    name='wrench',
    version=VERSION,
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='tools',
    test_suite='load_tests.get_suite',
    install_requires=install_requires,
)

if __name__ == '__main__':
    from setuptools import setup, find_packages

    SETUP_ARGS['packages'] = find_packages()
    setup(**SETUP_ARGS)
