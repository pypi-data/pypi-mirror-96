# Lilies

[![Build Status](https://travis-ci.org/mrz1988/lilies.svg?branch=master)](https://travis-ci.org/mrz1988/lilies)
[![Code Coverage](https://codecov.io/gh/mrz1988/lilies/branch/master/graphs/badge.svg)](https://codecov.io/gh/mrz1988/lilies/branch/master)

Lilies is currently in beta. Parts of the API are subject to change.

Lilies is a cross-platform, CLI text formatting and coloring tool for python. It automatically adjusts support for any console, including old Windows support powered by [colorama](https://pypi.org/project/colorama/). Lilies will attempt to reproduce the original colors as close as possible, regardless of the current terminal's capabilities.

Lilies is supported on python 3.5, 3.6, 3.7, and 3.8.

![Console demo](https://raw.githubusercontent.com/mrz1988/lilies/master/static/demo.svg)

## Getting started
Install us via [pip](https://pypi.org/project/lilies/)!
```
pip install lilies
```

To test color support in your console:
```python
>>> import lilies
>>> lilies.print_test()
```

Here's what that looks like in true color terminals:

![Console demo true color](https://raw.githubusercontent.com/mrz1988/lilies/master/static/truecolor.svg)


And in 256 color terminals:

![Console demo 256 color](https://raw.githubusercontent.com/mrz1988/lilies/master/static/256color.svg)

## Alternatives

| Library | 256 Color Support | True Color Support | Windows Support | Platform-specific coloring | len() adjustments | Formatting tools |
|----|----|----|----|----|----|----|
|lilies|✅|✅|✅|✅|✅|✅|
|[colorful](https://github.com/timofurrer/colorful)|✅|✅|⚠️|✅|✅|❌|
|[colored](https://pypi.org/project/colored/)|✅|❌|❌|❌|❌|❌|
|[colorama](https://github.com/tartley/colorama)|❌|❌|✅|❌|❌|❌|
|[termcolor](https://pypi.org/project/termcolor/)|❌|❌|❌|❌|❌|❌|

⚠️: colorful has newer Windows 10 support, but no support for old versions.

## Contributing
You can find information about contributing [here](https://github.com/mrz1988/lilies/blob/master/docs/contributing.rst)

## License
[MIT](https://github.com/mrz1988/lilies/blob/master/LICENSE)
