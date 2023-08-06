# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logdir']

package_data = \
{'': ['*']}

install_requires = \
['dulwich>=0.20.0', 'ruamel.yaml>0.15', 'toml>=0.10']

setup_kwargs = {
    'name': 'logdir',
    'version': '0.9.3',
    'description': 'A utility for managing logging directories.',
    'long_description': '# LogDir\n\nA utility for managing logging directories.\n\n|                    Source                    |                                                  PyPI                                                  |                                                                                             CI/CD                                                                                             |                        Docs                        |                                                                         Docs Status                                                                         |\n| :------------------------------------------: | :----------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------: |\n| [GitHub](https://github.com/btjanaka/logdir) | [![PyPI](https://img.shields.io/pypi/v/logdir?style=flat&color=blue)](https://pypi.org/project/logdir) | [![Test and Deploy](https://github.com/btjanaka/logdir/workflows/Test%20and%20Deploy/badge.svg?branch=master)](https://github.com/btjanaka/logdir/actions?query=workflow%3A"Test+and+Deploy") | [logdir.btjanaka.net](https://logdir.btjanaka.net) | [![Netlify Status](https://api.netlify.com/api/v1/badges/b3cdff86-dfcf-4b62-9a64-ab431bc5040f/deploy-status)](https://app.netlify.com/sites/logdir/deploys) |\n\n## Installation\n\nTo install from PyPI, run:\n\n```bash\npip install logdir\n```\n\nTo install from Conda, run:\n\n```bash\nconda install -c conda-forge logdir\n```\n\nTo install from source, clone this repo, cd into it, and run:\n\n```bash\npip install .\n```\n\nlogdir is tested on Python 3.7+. Earlier Python versions may work but are not\nguaranteed.\n\n## Usage\n\nIf your experiment is called `My Experiment`, you can create a logging directory\nfor it with:\n\n```python\nfrom logdir import LogDir\n\nlogdir = LogDir("My Experiment")\n```\n\nThis will create a logging directory of the form\n`./logs/YYYY-MM-DD_HH-MM-SS_my-experiment-dir`; you can change `./logs` by\npassing in a second argument for the root directory when initializing `LogDir`,\ni.e. `LogDir("My Experiment", "./different-log-dir")`.\n\nYou now have access to useful methods for creating files and saving data in the\ndirectory. For example, start writing to a file `new.txt` in the directory with:\n\n```python\nwith logdir.pfile("new.txt").open() as file:\n    file.write("Hello World!")\n```\n\nThis takes advantage of the [pfile()](/api/#logdir.LogDir.pfile) method, which\ncreates a `pathlib.Path` to the new file. It also uses `pathlib.Path.open()`.\n\n`pfile()` will also create intermediate directories, so this will work even if\n`foo/bar/` does not exist in the logging directory already:\n\n```python\nwith logdir.pfile("foo/bar/new.txt").open() as file:\n    file.write("Hello World!")\n```\n\nThere is also [save_data()](/api/#logdir.LogDir.save_data), which saves data to\na file. JSON, YAML, TOML, and pickle files are currently supported.\n\n```python\nlogdir.save_data({"a": 1, "b": 2, "c": 3}, "file.json")\n```\n\nFinally, [readme()](/api/#logdir.LogDir.readme) adds a README.md to the\ndirectory with multiple pieces of information. For instance, this command:\n\n```python\nlogdir.readme(date=True, git_commit=True)\n```\n\nWill create something like:\n\n```md\n# My Experiment\n\n- Date: 2020-10-04 23:04:05\n- Git Commit: e3rftyt543rt5y67jhtgr4yhju\n```\n',
    'author': 'Bryon Tjanaka',
    'author_email': 'bryon@btjanaka.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://logdir.btjanka.net',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
