# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wemake_python_styleguide',
 'wemake_python_styleguide.compat',
 'wemake_python_styleguide.logic',
 'wemake_python_styleguide.logic.arguments',
 'wemake_python_styleguide.logic.complexity',
 'wemake_python_styleguide.logic.naming',
 'wemake_python_styleguide.logic.scopes',
 'wemake_python_styleguide.logic.tokens',
 'wemake_python_styleguide.logic.tree',
 'wemake_python_styleguide.options',
 'wemake_python_styleguide.presets',
 'wemake_python_styleguide.presets.topics',
 'wemake_python_styleguide.presets.types',
 'wemake_python_styleguide.transformations',
 'wemake_python_styleguide.transformations.ast',
 'wemake_python_styleguide.violations',
 'wemake_python_styleguide.visitors',
 'wemake_python_styleguide.visitors.ast',
 'wemake_python_styleguide.visitors.ast.complexity',
 'wemake_python_styleguide.visitors.ast.naming',
 'wemake_python_styleguide.visitors.filenames',
 'wemake_python_styleguide.visitors.tokenize']

package_data = \
{'': ['*']}

install_requires = \
['astor>=0.8,<0.9',
 'attrs',
 'darglint>=1.2,<2.0',
 'flake8-bandit>=2.1,<3.0',
 'flake8-broken-line>=0.3,<0.4',
 'flake8-bugbear>=20.1,<21.0',
 'flake8-commas>=2.0,<3.0',
 'flake8-comprehensions>=3.1,<4.0',
 'flake8-debugger>=4.0,<5.0',
 'flake8-docstrings>=1.3,<2.0',
 'flake8-eradicate>=1.0,<2.0',
 'flake8-isort>=4.0,<5.0',
 'flake8-quotes>=3.0,<4.0',
 'flake8-rst-docstrings>=0.0.14,<0.0.15',
 'flake8-string-format>=0.3,<0.4',
 'flake8>=3.7,<4.0',
 'pep8-naming>=0.11,<0.12',
 'pygments>=2.4,<3.0',
 'typing_extensions>=3.6,<4.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata']}

entry_points = \
{'flake8.extension': ['WPS = wemake_python_styleguide.checker:Checker'],
 'flake8.report': ['wemake = '
                   'wemake_python_styleguide.formatter:WemakeFormatter']}

setup_kwargs = {
    'name': 'wemake-python-styleguide',
    'version': '0.15.2',
    'description': 'The strictest and most opinionated python linter ever',
    'long_description': '# wemake-python-styleguide\n\n[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake.services)\n[![Supporters](https://img.shields.io/opencollective/all/wemake-python-styleguide.svg?color=gold&label=supporters)](https://opencollective.com/wemake-python-styleguide)\n[![Build Status](https://github.com/wemake-services/wemake-python-styleguide/workflows/test/badge.svg?branch=master&event=push)](https://github.com/wemake-services/wemake-python-styleguide/actions?query=workflow%3Atest)\n[![codecov](https://codecov.io/gh/wemake-services/wemake-python-styleguide/branch/master/graph/badge.svg)](https://codecov.io/gh/wemake-services/wemake-python-styleguide)\n[![Python Version](https://img.shields.io/pypi/pyversions/wemake-python-styleguide.svg)](https://pypi.org/project/wemake-python-styleguide/)\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\n---\n\nWelcome to the strictest and most opinionated python linter ever.\n\n<p align="center">\n  <a href="https://wemake-python-stylegui.de">\n    <img src="https://raw.githubusercontent.com/wemake-services/wemake-python-styleguide/master/docs/_static/logo.png"\n         alt="wemake-python-styleguide logo">\n  </a>\n</p>\n\n`wemake-python-styleguide` is actually a [flake8](http://flake8.pycqa.org/en/latest/)\nplugin with [some other plugins](https://wemake-python-stylegui.de/en/latest/pages/usage/violations/index.html#external-plugins) as dependencies.\n\n\n## Quickstart\n\n```bash\npip install wemake-python-styleguide\n```\n\nYou will also need to create a `setup.cfg` file with the [configuration](https://wemake-python-stylegui.de/en/latest/pages/usage/configuration.html).\n\nWe highly recommend to also use:\n\n- [flakehell](https://wemake-python-stylegui.de/en/latest/pages/usage/integrations/flakehell.html) for easy integration into a **legacy** codebase\n- [nitpick](https://wemake-python-stylegui.de/en/latest/pages/usage/integrations/nitpick.html) for sharing and validating configuration across multiple projects\n\n\n## Running\n\n```bash\nflake8 your_module.py\n```\n\nThis app is still just good old `flake8`!\nAnd it won\'t change your existing workflow.\n\n<p align="center">\n  <img src="https://raw.githubusercontent.com/wemake-services/wemake-python-styleguide/master/docs/_static/running.png"\n       alt="invocation results">\n</p>\n\nSee ["Usage" section](https://wemake-python-stylegui.de/en/latest/pages/usage/setup.html)\nin the docs for examples and integrations.\n\nWe also support [GitHub Actions](https://wemake-python-stylegui.de/en/latest/pages/usage/integrations/github-actions.html) as first class-citizens.\n[Try it out](https://github.com/marketplace/actions/wemake-python-styleguide)!\n\n\n## What we are about\n\nThe ultimate goal of this project is\nto make all people write **exactly** the same `python` code.\n\n|                            | flake8 | pylint | black | mypy | wemake-python-styleguide |\n|----------------------------|--------|--------|-------|------|--------------------------|\n| Formats code?              |   ❌   |   ❌   |   ✅  |  ❌  |            ❌           |\n| Finds style issues?        |   🤔   |   ✅   |   🤔  |  ❌  |            ✅           |\n| Finds bugs?                |   🤔   |   ✅   |   ❌  |  ✅  |            ✅           |\n| Finds complex code?        |   ❌   |   🤔   |   ❌  |  ❌  |            ✅           |\n| Has a lot of strict rules? |   ❌   |   🤔   |   ❌  |  ❌  |            ✅           |\n| Has a lot of plugins?      |   ✅   |   ❌   |   ❌  |  🤔  |            ✅           |\n\nWe have several primary objectives:\n\n0. Enforce `python3.6+` usage\n1. Significantly reduce complexity of your code and make it more maintainable\n2. Enforce "There should be one -- and preferably only one -- obvious way to do it" rule to coding and naming styles\n3. Protect developers from possible errors and enforce best practices\n\nYou can find all error codes and plugins [in the docs](https://wemake-python-stylegui.de/en/latest/pages/usage/violations/index.html).\n\n\n## What we are not\n\nWe are *not* planning to do the following things:\n\n0. Assume or check types, use `mypy` together with our linter\n1. [Reformat code](https://wemake-python-stylegui.de/en/latest/pages/usage/integrations/auto-formatters.html), since we believe that developers should do that\n2. Check for `SyntaxError` or logical bugs, write tests instead\n3. Appeal to everyone. But, you can [switch off](https://wemake-python-stylegui.de/en/latest/pages/usage/setup.html#ignoring-violations) any rules that you don\'t like\n\n\n## Supporting us :tada:\n\nWe in [wemake.services](https://wemake.services) make\nall our tools open-source by default, so the community can benefit from them.\nIf you use our tools and they make your life easier and brings business value,\nyou can return us a favor by supporting the work we do.\n\n[![Gold Tier](https://opencollective.com/wemake-python-styleguide/tiers/gold-sponsor.svg?width=890)](https://opencollective.com/wemake-python-styleguide)\n\n[![Silver Tier](https://opencollective.com/wemake-python-styleguide/tiers/silver-sponsor.svg?width=890&avatarHeight=45&button=0)](https://opencollective.com/wemake-python-styleguide)\n\n[![Bronze Tier](https://opencollective.com/wemake-python-styleguide/tiers/bronze-sponsor.svg?width=890&avatarHeight=35&button=0)](https://opencollective.com/wemake-python-styleguide)\n\n\n## Show your style :sunglasses:\n\nIf you use our linter - it means that your code is awesome.\nYou can be proud of it!\nAnd you should share your accomplishment with others\nby including a badge to your `README` file. It looks like this:\n\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n\n### Markdown\n\n```md\n[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)\n```\n\n### Restructured text\n\n```rst\n.. image:: https://img.shields.io/badge/style-wemake-000000.svg\n   :target: https://github.com/wemake-services/wemake-python-styleguide\n```\n\n\n## Contributing\n\nWe **warmly welcome** all contributions!\n\n[![List of contributors](https://opencollective.com/wemake-python-styleguide/contributors.svg?width=890&button=0)](https://github.com/wemake-services/wemake-python-styleguide/graphs/contributors)\n\nSee ["Contributing"](https://wemake-python-stylegui.de/en/latest/pages/api/index.html#contributing) section in the documentation if you want to contribute.\n\nYou can start with [issues that need some help](https://github.com/wemake-services/wemake-python-styleguide/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)\nright now.\n',
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://wemake-python-stylegui.de',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
