# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fhmake']

package_data = \
{'': ['*']}

install_requires = \
['tomlkit>=0.7.0,<2']

extras_require = \
{'full': ['simplesecurity>=2021.2,<2023',
          'checkrequirements>=2021,<2023',
          'poetry>=1.1.2,<3',
          'licensecheck>=2021.1,<2023',
          'fhdoc>=2021,<2023',
          'radon>=4.3.2,<6']}

entry_points = \
{'console_scripts': ['fhmake = fhmake:cli']}

setup_kwargs = {
    'name': 'fhmake',
    'version': '2021',
    'description': 'Provides multiple methods to hide and retrieve data',
    'long_description': '[![GitHub top language](https://img.shields.io/github/languages/top/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../)\n[![Repository size](https://img.shields.io/github/repo-size/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../)\n[![Issues](https://img.shields.io/github/issues/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../issues)\n[![License](https://img.shields.io/github/license/FHPythonUtils/FHMake.svg?style=for-the-badge)](/LICENSE.md)\n[![Commit activity](https://img.shields.io/github/commit-activity/m/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../commits/master)\n[![Last commit](https://img.shields.io/github/last-commit/FHPythonUtils/FHMake.svg?style=for-the-badge)](../../commits/master)\n[![PyPI Downloads](https://img.shields.io/pypi/dm/fhmake.svg?style=for-the-badge)](https://pypistats.org/packages/fhmake)\n[![PyPI Total Downloads](https://img.shields.io/badge/dynamic/json?style=for-the-badge&label=total%20downloads&query=%24.total_downloads&url=https%3A%2F%2Fapi.pepy.tech%2Fapi%2Fprojects%2Ffhmake)](https://pepy.tech/project/fhmake)\n[![PyPI Version](https://img.shields.io/pypi/v/fhmake.svg?style=for-the-badge)](https://pypi.org/project/fhmake)\n\n<!-- omit in toc -->\n# FHMake\n\n<img src="readme-assets/icons/name.png" alt="Project Icon" width="750">\n\nFredHappyface Makefile for python. Run one of the following subcommands...\n\ninstall: Poetry install\nbuild: Build documentation, requirements.txt, and run poetry build\npublish: Run poetry publish (interactive)\naudit: dependency checking, security analysis and complexity/ Maintainability\nchecking. Use with --fast to speed up the security analysis.\n\n<!-- omit in toc -->\n## Table of Contents\n- [Documentation](#documentation)\n- [Install With PIP](#install-with-pip)\n- [Language information](#language-information)\n\t- [Built for](#built-for)\n- [Install Python on Windows](#install-python-on-windows)\n\t- [Chocolatey](#chocolatey)\n\t- [Download](#download)\n- [Install Python on Linux](#install-python-on-linux)\n\t- [Apt](#apt)\n- [How to run](#how-to-run)\n\t- [With VSCode](#with-vscode)\n\t- [From the Terminal](#from-the-terminal)\n- [Download Project](#download-project)\n\t- [Clone](#clone)\n\t\t- [Using The Command Line](#using-the-command-line)\n\t\t- [Using GitHub Desktop](#using-github-desktop)\n\t- [Download Zip File](#download-zip-file)\n- [Community Files](#community-files)\n\t- [Licence](#licence)\n\t- [Changelog](#changelog)\n\t- [Code of Conduct](#code-of-conduct)\n\t- [Contributing](#contributing)\n\t- [Security](#security)\n\t- [Support](#support)\n\t- [Rationale](#rationale)\n\n\n## Documentation\nSee the [Docs](/DOCS/) for more information.\n\n## Install With PIP\n\n**"Slim" Build:** Install simplesecurity\\[full\\], poetry, checkrequirements\\[full\\]\nand licensecheck\\[full\\] with pipx\n\n```python\npip install fhmake\n```\n\n**Otherwise:**\n```python\npip install fhmake[full]\n```\n\nHead to https://pypi.org/project/fhmake/ for more info\n\n## Language information\n### Built for\nThis program has been written for Python 3 and has been tested with\nPython version 3.9.0 <https://www.python.org/downloads/release/python-380/>.\n\n## Install Python on Windows\n### Chocolatey\n```powershell\nchoco install python\n```\n### Download\nTo install Python, go to <https://www.python.org/> and download the latest\nversion.\n\n## Install Python on Linux\n### Apt\n```bash\nsudo apt install python3.9\n```\n\n## How to run\n### With VSCode\n1. Open the .py file in vscode\n2. Ensure a python 3.9 interpreter is selected (Ctrl+Shift+P > Python:Select\nInterpreter > Python 3.9)\n3. Run by pressing Ctrl+F5 (if you are prompted to install any modules, accept)\n### From the Terminal\n```bash\n./[file].py\n```\n\n## Download Project\n### Clone\n#### Using The Command Line\n1. Press the Clone or download button in the top right\n2. Copy the URL (link)\n3. Open the command line and change directory to where you wish to\nclone to\n4. Type \'git clone\' followed by URL in step 2\n```bash\n$ git clone https://github.com/FHPythonUtils/FHMake\n```\n\nMore information can be found at\n<https://help.github.com/en/articles/cloning-a-repository>\n\n#### Using GitHub Desktop\n1. Press the Clone or download button in the top right\n2. Click open in desktop\n3. Choose the path for where you want and click Clone\n\nMore information can be found at\n<https://help.github.com/en/desktop/contributing-to-projects/cloning-a-repository-from-github-to-github-desktop>\n\n### Download Zip File\n\n1. Download this GitHub repository\n2. Extract the zip archive\n3. Copy/ move to the desired location\n\n## Community Files\n### Licence\nMIT License\nCopyright (c) FredHappyface\n(See the [LICENSE](/LICENSE.md) for more information.)\n\n### Changelog\nSee the [Changelog](/CHANGELOG.md) for more information.\n\n### Code of Conduct\nOnline communities include people from many backgrounds. The *Project*\ncontributors are committed to providing a friendly, safe and welcoming\nenvironment for all. Please see the\n[Code of Conduct](https://github.com/FHPythonUtils/.github/blob/master/CODE_OF_CONDUCT.md)\n for more information.\n\n### Contributing\nContributions are welcome, please see the\n[Contributing Guidelines](https://github.com/FHPythonUtils/.github/blob/master/CONTRIBUTING.md)\nfor more information.\n\n### Security\nThank you for improving the security of the project, please see the\n[Security Policy](https://github.com/FHPythonUtils/.github/blob/master/SECURITY.md)\nfor more information.\n\n### Support\nThank you for using this project, I hope it is of use to you. Please be aware that\nthose involved with the project often do so for fun along with other commitments\n(such as work, family, etc). Please see the\n[Support Policy](https://github.com/FHPythonUtils/.github/blob/master/SUPPORT.md)\nfor more information.\n\n### Rationale\nThe rationale acts as a guide to various processes regarding projects such as\nthe versioning scheme and the programming styles used. Please see the\n[Rationale](https://github.com/FHPythonUtils/.github/blob/master/RATIONALE.md)\nfor more information.\n',
    'author': 'FredHappyface',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FHPythonUtils/FHMake',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
