# Installation

`pip3 install dplot`

# Usage examples

## `crysol` output

```bash
dplot "out/crysol.png" --other "in/crysol.int" \
    --headers "Q,Intensity,Scattering (in vacuo),Scattering (excluded volume),Convex border layer" \
    --skip 1 -x "Q" --log
```

or

```bash
dplot "out/crysol.png" --crysol "in/crysol.int"
```

![crysol](out.reference/crysol.png)

## `debyer` output

```bash
dplot "out/debyer.png" --other "in/debyer.dat" --skip 2 --headers "Q,Intensity" -x "Q" --log
```

or

```bash
dplot "out/debyer.png" --debyer "in/debyer.dat"
```

![debyer](out.reference/debyer.png)

## `psaxs` output

```bash
dplot "out/psaxs.png" --other "in/psaxs.tsv" --headers "Q,Intensity" -x "Q" --log
```

or

```bash
dplot "out/psaxs.png" --psaxs "in/psaxs.tsv"
```

![psaxs](out.reference/psaxs.png)

## Multiple sources

```bash
./dplot.py "out/combined.png" --psaxs "in/psaxs.tsv" --crysol "in/crysol.int" --debyer "in/debyer.dat"
```

Mixing manual plots with presets works as well

```bash
./dplot.py "out/combined.png" --other "in/psaxs.tsv" --headers "Q,Intensity" -x "Q" --crysol "in/crysol.int" --debyer "in/debyer.dat"
```

![combined](out.reference/combined.png)

## Window

Provide `-` instead of a file name to open a window

```bash
dplot - --psaxs "in/psaxs.tsv"
```

![window](out.reference/window.png)

## Possible options

Unfortunately `--help` won't work.

Use `--verbose` to see possible switches.


# Development

## Dependencies

- `pandas`
- `seaborn`
- `matplotlib`
- Python 3.6 - 3.9

With _pyenv_ or _conda_

```
python3 -m pip install pandas seaborn matplotlib
```

## Clone

```shell
git clone git@gitlab.com:cbjh/plotting/dplot.git
```

## Install

```shell
cd dplot
python3 -m pip install -e .
```

Files in `dplot` folder can be edited without need for re-installation.

Re-installation still needs to be done if the folder is moved somewhere else

```shell
python3 -m pip uninstall dplot
cd dplot
python3 -m pip install -e .
```

# Tests

```bash
sudo apt install imagemagick
```

```bash
python3 -m pip install -e .
./test.sh
```

Keep in mind that this overrides your locally installed `dplot`.

# Packaging

## Prerequisites

```shell
sudo apt-get install python3-venv
python3 -m pip install --upgrade build twine
```

## Publishing

Review `setup.py`, in particular change the version.

```shell
python3 -m build
python3 -m twine upload --repository pypi dist/*
```

(it asks for PyPI credentials)
