from setuptools import setup
import glob
import os
import sys

def package_files(package_dir, subdirectory):
    # walk the input package_dir/subdirectory
    # return a package_data list
    paths = []
    directory = os.path.join(package_dir, subdirectory)
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            path = path.replace(package_dir + '/', '')
            paths.append(os.path.join(path, filename))
    return paths


data_files = package_files('sortrobot', 'data')

setup_args = {
    'name': 'sortrobot',
    'author': 'Aaron Parsons and Judah Spiegel',
    'url': 'https://github.com/AaronParsons/sortrobot',
    'license': 'BSD',
    'description': 'control software for a card-sorting robot.',
    'package_dir': {'sortrobot': 'sortrobot'},
    'packages': ['sortrobot'],
    'include_package_data': True,
    'scripts': glob.glob('scripts/*.py'),
    'version': '0.0.1',
    'package_data': {'sortrobot': data_files},
    'zip_safe': False,
}


if __name__ == '__main__':
    setup(*(), **setup_args)
