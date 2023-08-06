# MultiTech Multitool Utility

Library and command line tool for working with Multitech products.

## Usage

Command line tool `multitool` has functionality split into subcommands.  To get a list of valid subcommands use `--help`
or `-h`.  Each subcommand can also be queried for details using `--help`.

### Examples

Get help:
```
multitool --help
multitool device --help
multitool device patch --help
```

#### Device Subcommand

The `device` command has tools for packaging device firmware upgrades.

Create a patch for an MDot when the images contain bootloaders:
```
multitool device patch -m -V 4.0.2 -v 4.0.5 -i MTDOT -b mdot_image_4.0.2.bin mdot_image_4.0.5.bin
```

Compress an XDot image which does not contain a bootloader and append a CRC32:
```
multitool device compress -m -c -i XDOT xdot_image_4.0.5_application.bin
```

Upgrade an mDot over serial with an image that contains a bootloader:
```
multitool device upgrade -b COM3 MTDOT mdot_image_4.0.5.bin
```

#### Version Number Format

Version numbers can be four parts.  When specified as rc, beta, or alpha only three parts can be included.
* 1.2
* 1.2.3.4
* 1.2-rc4
* 1.2-beta4
* 1.2-alpha4

## Installation 
Use PIP to install, the `multitool` executable will be added to the Python scripts directory.

```
pip install mtsmultitool
```
## Change Log

### v0.2
* Change device model to series, supported series are MTDOT, MDOT, XDOT, MTQ, and MTQN.
* Automatically determine application offset for `-b` option based on specified device series.
* Added ability to upgrade a device over serial, it must have MultiTech's bootloader.
* Added additional fields to manifest to support future versions of FOTA
* Added and modified CLI options for changes to manifest 

[//]: # (End long description)

From local source:
```
pip install -e . mtsmultitool
```

## Building Distributions

Run the following command to build a source distribution which requires compiling when installed by PIP.

```
python setup.py sdist
```

Run the following command on each platform to build a pre-compiled distribution.  Note the distribution will only be
valid for the python version used.  Separate builds must be created for each version of Python supported, including
32-bit and 64-bit.

```
python setup.py sdist bdist_wheel
```

## Running Tests

Install `tox` with `pip install tox`.

Execute the following command to run tests:
```
tox
```

## Building Documentation

Module and command interface documentation is located in `docs` and is built using [Sphinx](https://www.sphinx-doc.org/en/master/index.html).

Install the `mtsmultitool` package and follow instruction for [installing Sphinx](https://www.sphinx-doc.org/en/master/usage/installation.html).

To build HTML documentation:
```
cd docs
make html
```
