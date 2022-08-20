import subprocess
import time

from setuptools import setup, find_packages


def get_rev():
    output = subprocess.run(
        ['git', 'rev-parse', '--short', 'HEAD'],
        stdout=subprocess.PIPE,
        check=True)
    return output.stdout.decode('utf-8').strip()


def get_date_string():
    return time.strftime('%Y.%-m.%-d')


setup(
    name='shelly-ota',
    version=f'{get_date_string()}+{get_rev()}',
    url='https://github.com/bpetrikovics/shelly-ota',
    license='MIT',
    author='Balazs Petrikovics',
    author_email='bpetrikovics@gmail.com',
    description='OTA upgrade tool for Shelly IoT devices ',
    install_requires=[
        'requests',
        'netifaces'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'shelly-ota=shelly_ota.main:main',
        ]
    },
)
