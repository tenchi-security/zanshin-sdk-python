from pathlib import Path
from os.path import join
import re

from setuptools import setup

def get_version():
    version_py = join('zanshinsdk','version.py')
    regex = re.compile('__version__\s*=\s*[\'\"](?P<version>[\d\.]+)')
    return regex.finditer(open(version_py, 'r', encoding='utf8').read()).__next__().group('version')

extras = {
    'with_boto3': ['boto3>=1.21.21']
}

setup(
    name='zanshinsdk',
    description='Python SDK to access the Tenchi Security Zanshin API v1',
    long_description=Path('README.rst').read_text(encoding="utf8"),
    author='Tenchi Security',
    author_email='contact@tenchisecurity.com',
    version=get_version(),
    url='https://github.com/tenchi-security/zanshin-sdk-python',
    license='Apache Software License',
    install_requires=['httpx==0.23.0'],
    tests_require=['pytest==7.1.1', 'moto[all]==3.1.1'],
    setup_requires=['pytest-runner==6.0.0'],
    packages=['zanshinsdk'],
    extras_require=extras,
    # include_package_data=True,
    platforms='any',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
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
    ]
)
# flake8: noqa
