"""
Setup Module to setup Python Handlers for ballet-assemble.
"""
import os

from setupbase import (
    create_cmdclass, install_npm, ensure_targets,
    combine_commands, ensure_python
)
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

# Ensure a valid python version
ensure_python('>=3.6')

# Representative files that should exist after a successful build
jstargets = [
    os.path.join(HERE, 'lib', 'serverextension.js'),
]

package_data_spec = {
    'ballet_assemble': [
        '*'
    ]
}

data_files_spec = [
    (
        'share/jupyter/lab/extensions',
        os.path.join(HERE, 'server', 'ballet_assemble', 'labextension'),
        '*.tgz',
    ),
    (
        'etc/jupyter/jupyter_notebook_config.d',
        os.path.join(HERE, 'server', 'jupyter-config'),
        'ballet-assemble.json',
    ),
]

cmdclass = create_cmdclass(
    prerelease_cmd='jsdeps',
    package_data_spec=package_data_spec,
    data_files_spec=data_files_spec
)

cmdclass['jsdeps'] = combine_commands(
    install_npm(HERE, build_cmd='build:all', npm=['jlpm']),
    ensure_targets(jstargets),
)

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'ballet',
    'black == 19.10b0',
    'funcy',
    'gitpython',
    'jupyterlab ~= 2.0',
    'notebook',
    'pygithub',
    'requests',
    'stacklog',
    'tenacity',
    'tornado',
]

test_requirements = [
    'coverage >= 4.5.1',
    'pytest >= 3.4.2',
    'pytest-cov >= 2.6',
]

development_requirements = [
    # general
    'bump2version >= 1.0.0',
    'pip >= 9.0.1',

    # style check
    'flake8 >= 3.5.0',
    'isort >= 4.3.4, <= 4.3.9',

    # distribute on PyPI
    'twine >= 1.10.0',
    'wheel >= 0.30.0',
]

setup_args = dict(
    name='ballet-assemble',
    version='0.8.3',
    url='https://github.com/HDI-Project/ballet-assemble',
    author='Micah Smith',
    description='Submit ballet modules from within JupyterLab',
    long_description=long_description,
    long_description_content_type='text/markdown',
    cmdclass=cmdclass,
    packages=find_packages(where='server',
                           include=['ballet_assemble',
                                    'ballet_assemble.*']),
    package_dir={'': 'server'},
    install_requires=install_requires,
    extras_require={
        'test': test_requirements,
        'dev': development_requirements + test_requirements,
    },
    zip_safe=False,
    include_package_data=True,
    license='MIT',
    platforms='Linux, Mac OS X, Windows',
    keywords=['Jupyter', 'JupyterLab'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Framework :: Jupyter',
    ],
)

if __name__ == '__main__':
    setup(**setup_args)
