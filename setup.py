try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'PyFicr - Get a printable of FICR pages',
    'author': 'Andrea Pavan',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'prog.pawz at gmail dot com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': 'pyficr',
    'scripts': ['pyficr/pyficr.py'],
    'name': 'pyficr',
}

setup(**config)
