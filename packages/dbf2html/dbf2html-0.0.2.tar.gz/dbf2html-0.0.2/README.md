[![PyPI](https://img.shields.io/pypi/v/dbf2html.svg)](https://pypi.org/project/dbf2html/) <img src="https://github.com/Yangzhenzhao/dbf2html/workflows/CI/badge.svg" />


### Installation

`pip install --upgrade dbf2html`        


### Cli

```
$ dbf2html --help                                                             
Usage: dbf2html [OPTIONS] FILEPATH

Options:
  -e, --encoding TEXT
  -o, --output TEXT
  -t, --title TEXT
  --help               Show this message and exit.

$ dbf2html test.dbf
$ dbf2html test.dbf -o mytest.html
$ dbf2html test.dbf -o mytest.html --title testdbf_show
```
