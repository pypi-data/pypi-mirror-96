# Kouyierr (Arthouuur)

[![GitHub tag](https://img.shields.io/github/tag/vmdude/kouyierr.svg)](https://github.com/vmdude/kouyierr/tags/)
[![GitHub license](https://img.shields.io/github/license/vmdude/kouyierr.svg)](https://github.com/vmdude/kouyierr/blob/main/LICENSE)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/kouyierr.svg)](https://pypi.org/project/kouyierr/)
[![CircleCI](https://circleci.com/gh/vmdude/kouyierr.svg?style=shield&circle-token=bb402d38d6d34114914609699878802d86235c9a)](https://circleci.com/gh/vmdude/kouyierr)

![Kouyierr](logo.jpg)

This project is basically a document generator (Doc As Code) focused on a few targets like invoices, timesheet, resume or documentation.

The initial goal was to avoid using Microsoft Wo@#$ and Ex@#$ to generate these recurrent documents, and to be able to add a little automation (of course we're lazy ^^).

## Usage

This python module use `click` to facilitate cli calls, help is self-explanatory:

```bash
kouyierr --help
Usage: kouyierr [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  documentation
  invoice
  version
```

We use [rich](https://github.com/willmcgugan/rich) Python module to add some fancy console display as well:

![richsample](rich_sample.png)

## Scope

With `click` module, we bundled several scope to make life easier

### documentation

This scope let you generate PDF documentaion file based on markdown document.

```bash
kouyierr documentation generate --help
Usage: kouyierr documentation generate [OPTIONS]

  Generate a new documentation from Markdown file based on TeX template

Options:
  --output-dir TEXT   Output directory, default=.
  --markdown TEXT     Markdown file path to use for documentation  [required]
  --output-file TEXT  Output PDF filename, default=output.pdf
  --template TEXT     TeX template file path
  --help              Show this message and exit.
```

It can be summoned simply like:

```bash
cd tests/org_sample
kouyierr documentation generate --markdown README.md --template template.tex
```

Sample files can be found in this repo in the unittest folder:

- [README.md](tests/org_sample/README.md): Markdown source file
- [template.tex](tests/org_sample/template.tex): LaTex template
- [bottom.png](tests/org_sample/bottom.png): Image file used in LaTex template for bottom border

Generated file with these sample can also be found in this repo:

- [draft.pdf](data/documentation/draft.pdf): PDF file

### invoice

This scope let you generate HTML/PDF invoice file based on YAML definition file and Jinja2 template.

```bash
kouyierr invoice generate --help
Usage: kouyierr invoice generate [OPTIONS]

  Generate a new invoice based on definition file and company template

Options:
  --output-dir TEXT      Output directory, default=.
  --company_config TEXT  Company config file  [required]
  --invoice_config TEXT  Invoice config file  [required]
  --invoice_id TEXT      Invoice ID, default=all
  --template TEXT        Template file path  [required]
  --help                 Show this message and exit.
```

It can be summoned simply like:

```bash
kouyierr invoice generate --company_config tests/org_sample/myfancycompany.yml --invoice_config tests/org_sample/nicecustomer.yml --template tests/org_sample/myfancycompany.html.j2 # for bulk mode for all invoices from this client
kouyierr invoice generate --company_config tests/org_sample/myfancycompany.yml --invoice_config tests/org_sample/nicecustomer.yml --template tests/org_sample/myfancycompany.html.j2 --invoice_id 202011_CUS # for specific invoice
```

Sample files can be found in this repo in the unittest folder:

- [myfancycompany.html.j2](tests/org_sample/myfancycompany.html.j2): Jinja2 template
- [myfancycompany.yml](tests/org_sample/myfancycompany.yml): Company config file
- [nicecustomer.yml](tests/org_sample/nicecustomer.yml): Invoice config file

Generated file with these sample can also be found in this repo:

- [202011_CUS.html](data/invoice/202011_CUS.html): HTML file
- [202011_CUS.pdf](data/invoice/202011_CUS.pdf): PDF file

### resume

TODO

### timesheet

TODO

## How to build

```bash
# create a virtual env
virtualenv venv

# activate virtual env 
source venv/bin/activate 

# run test and package
pip3 install .[test] --user --upgrade
pip3 install .\[test\] --user --upgrade # for ZSH users
python3 setup.py test

# install snapshot build
pip3 install . --user --upgrade
```

## Releases

After a commit or merge on master [circleci](https://circleci.com/vmdude/kouyierr) deploys kouyierr automatically on [pypi](https://pypi.org/project/kouyierr/)

To install the release version from PyPi:

```bash
pip3 install kouyierr --upgrade --user
```

Or you can install local version as well:

```bash
git clone git@github.com:vmdude/kouyierr.git && cd kouyierr
pip3 install . --upgrade --user
```

## Docker image

For our unittests we built a docker image with requirements for kouyierr. You can use it as well from [this repo](https://github.com/vmdude/kouyierr-docker)

```bash
docker pull vmdude/kouyierr-docker
docker run -it vmdude/kouyierr-docker
```

## License

This project is licensed under the MIT License (see the
`LICENSE` file for details).
