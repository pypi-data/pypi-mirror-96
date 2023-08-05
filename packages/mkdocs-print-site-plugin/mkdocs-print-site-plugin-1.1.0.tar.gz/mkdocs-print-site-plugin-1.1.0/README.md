[![Actions Status](https://github.com/timvink/mkdocs-print-site-plugin/workflows/pytest/badge.svg)](https://github.com/timvink/mkdocs-print-site-plugin/actions)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-print-site-plugin)
![PyPI](https://img.shields.io/pypi/v/mkdocs-print-site-plugin)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-print-site-plugin)
[![codecov](https://codecov.io/gh/timvink/mkdocs-print-site-plugin/branch/master/graph/badge.svg)](https://codecov.io/gh/timvink/mkdocs-print-site-plugin)
![GitHub contributors](https://img.shields.io/github/contributors/timvink/mkdocs-print-site-plugin)
![PyPI - License](https://img.shields.io/pypi/l/mkdocs-print-site-plugin)

# mkdocs-print-site-plugin

[MkDocs](https://www.mkdocs.org/) plugin that adds a page to your site combining all pages, allowing your site visitors to *File > Print > Save as PDF* the entire site. See [demo](https://timvink.github.io/mkdocs-print-site-plugin/print_page.html).

## Features :star2:

- Allow visitors to create PDFs from MkDocs sites.
- Support for pagination in PDFs.
- Works on all MkDocs themes.
- Support for [mkdocs-material](https://github.com/squidfunk/mkdocs-material) features like instant loading and dark color themes.
- Options to add table of contents and enumeration to headings and figures.
- Option to add a cover page.
- Lightweight, no dependencies.

If you need to create PDFs programmatically, have a look at alternatives like [mkdocs-pdf-export-plugin](https://github.com/zhaoterryy/mkdocs-pdf-export-plugin) and [mkdocs-pdf-with-js-plugin](https://github.com/smaxtec/mkdocs-pdf-with-js-plugin).

## Setup

Install the plugin using `pip3`:

```bash
pip3 install mkdocs-print-site-plugin
```

Next, add the following lines to your `mkdocs.yml`:

```yml
plugins:
  - search
  - print-site
```

> ⚠️ Make sure to put `print-site` to the **bottom** of the plugin list. This is because other plugins might alter your site (like the navigation), and you want these changes included in the print page.

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.

## Documentation

Available at [timvink.github.io/mkdocs-print-site-plugin](https://timvink.github.io/mkdocs-print-site-plugin/).

## Contributing

Contributions are very welcome! Start by reading the [contribution guidelines](https://timvink.github.io/mkdocs-print-site-plugin/contributing.html).
