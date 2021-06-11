import io

from setuptools import setup
from zanshinsdk import __version__


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


setup(
    name='zanshinsdk',
    description='Python SDK to access the Tenchi Security Zanshin API v1',
    long_description=read('README.rst'),
    author='Tenchi Security',
    author_email='contact@tenchisecurity.com',
    version=__version__,
    url='https://github.com/tenchi-security/zanshin-sdk-python',
    license='Apache Software License',
    install_requires=['typer>=0.3.2','requests>=2.25,<3', 'types-requests>=0.1.8,<1', 'prettytable>=2.1,<3'],
    tests_require=['pytest>=6.2,<7', 'pandoc'],
    setup_requires=['pytest-runner>=5.3,<6'],
    packages=['zanshinsdk'],
    #include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries',
    ],
    entry_points={
        'console_scripts': ['zanshin=zanshinsdk.cli:main_app']
    }
)
