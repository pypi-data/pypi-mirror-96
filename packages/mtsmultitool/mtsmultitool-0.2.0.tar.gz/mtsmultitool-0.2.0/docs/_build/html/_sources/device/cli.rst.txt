******
device
******


.. code-block::

    multitool device [-h] CMD ...

**Subcommands**

keygen
    Create a key pair for signing a manifest.

keypub
    Export public key from a private key.

patch (pa)
    Create a firmware patch from old and new images.

compress (co)
    Compress a firmware image.

plain (pl)
    Create a plain firmware upgrade.

manifest (mf)
    Create a manifest for a firmware image.

combine (cb)
    Combine a manifest with a firmware image.

verify
    Verify signature and hash of a manifest or image with a manifest.

crc
    Add a CRC32 to an image.

upgrade
    Upgrade a device over serial.

help
    Show help message.

keygen
======

Usage
-----

.. code-block::

    multitool device keygen [-h] [-d DIR] name

positional arguments
^^^^^^^^^^^^^^^^^^^^

name
    Name of key

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    show this help message and exit

-d DIR, --dir DIR
    Directory path to save key files


keypub
======

Usage
-----

.. code-block::

    multitool device keypub [-h] [-f {hex,c}] [-o OUTPUT] priv_key_file

positional arguments
^^^^^^^^^^^^^^^^^^^^

priv_key_file
    Path to private key file

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    show this help message and exit

-f {hex,c}, --format {hex,c}
    Key output format

-o OUTPUT, --output OUTPUT
    Output file path



patch
=====

Usage
-----

.. code-block::

    multitool device patch [-h] [-m] [-d DESCRIPTION] [-i SERIES] [-I MODEL] [-v VERSION]
                           [-V REQUIRED_VERSION] [-n VENDOR] [-N VENDOR_DNS] [-s KEYFILE]
                           [-b] [-c] [-o OUTPUT] original upgrade


positional arguments
^^^^^^^^^^^^^^^^^^^^

original
    Path to original firmware image

upgrade
    Path to upgrade firmware image

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    Show help message

-m, --manifest
    Add a manifest to patch image, requires version and class description arguments

-d DESCRIPTION, --description DESCRIPTION
    Description of upgrade

-i SERIES, --series SERIES
    Target hardware series

-I MODEL, --model MODEL
    A more precise hardware description than the series

-v VERSION, --version VERSION
    Firmware version in upgrade

-V REQUIRED_VERSION, --required-version REQUIRED_VERSION
    Version of original firmware

-n VENDOR, --vendor VENDOR
    Vendor DNS used to create vendor-id in manifest.

-N VENDOR_DNS, --vendor-dns VENDOR_DNS
    Vendor DNS used to create vendor-id in manifest.

-s KEYFILE, --sign KEYFILE
    Sign manifest with the specified private key

-b, --bootloader
    Images contain a bootloader, application offset is determined by series

-c, --crc
    Append CRC32 to end of output file

-o OUTPUT, --output OUTPUT
    Output file path

Examples
--------

Create a patch to upgrade an MDot from 4.0.4 to 4.0.5 from images containing a bootloader and sign the manifest::

    multitool device patch -m -v 4.0.5 -V 4.0.4 -i MTDOT -s mykey.prv -b mdot_image_4.0.4.bin mdot_image_4.0.5.bin

Create a patch to upgrade an XDot from 4.0.4 to 4.0.5 from images containing a bootloader and sign the manifest::

    multitool device patch -m -v 4.0.5 -V 4.0.4 -d XDOT -s mykey.prv -b xdot_image_4.0.4.bin xdot_image4.0.5.bin


compress
========

Usage
-----

.. code-block::

    multitool device compress [-h] [-m] [-d DESCRIPTION] [-i SERIES] [-I MODEL] [-v VERSION]
                              [-n VENDOR] [-N VENDOR_DNS] [-s KEYFILE] [-b] [-c] [-o OUTPUT] image

positional arguments
^^^^^^^^^^^^^^^^^^^^

image
    Path to firmware image

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    show this help message and exit

-m, --manifest
    Add a manifest to compressed image

-d DESCRIPTION, --description DESCRIPTION
    Description of upgrade

-i SERIES, --series SERIES
    Target hardware series

-I MODEL, --model MODEL
    A more precise hardware description than the series

-v VERSION, --version VERSION
    Firmware version in upgrade

-n VENDOR, --vendor VENDOR
    Vendor DNS used to create vendor-id in manifest.

-N VENDOR_DNS, --vendor-dns VENDOR_DNS
    Vendor DNS used to create vendor-id in manifest.

-s KEYFILE, --sign KEYFILE
    Sign manifest with the specified private key

-b, --bootloader
    Images contain a bootloader, application offset is determined by series

-c, --crc
    Append CRC32 to end of output file

-o OUTPUT, --output OUTPUT
    Output file path


Examples
--------

Create a compressed upgrade for MDot from an image containing a bootloader and sign the manifest::

    multitool device compress -m -i MTDOT -s mykey.prv -b mdot_image_4.0.5.bin

Create a compressed upgrade for XDot from an image containing a bootloader and sign the manifest::

    multitool device compress -m -i XDOT -s mykey.prv -b xdot_image_4.0.5.bin

plain
=====

Usage
-----

.. code-block::

    multitool device plain [-h] [-m] [-d DESCRIPTION] [-i SERIES] [-I MODEL] [-v VERSION] [-n VENDOR]
                           [-N VENDOR_DNS] [-s KEYFILE] [-b] [-c] [-o OUTPUT] image

positional arguments
^^^^^^^^^^^^^^^^^^^^

image
    Path to firmware image

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    show this help message and exit

-m, --manifest
    Add a manifest to patch image.

-d DESCRIPTION, --description DESCRIPTION
    Description of upgrade

-i SERIES, --series SERIES
    Target hardware series

-I MODEL, --model MODEL
    A more precise hardware description than the series

-v VERSION, --version VERSION
    Firmware version in upgrade

-n VENDOR, --vendor VENDOR
    Vendor DNS used to create vendor-id in manifest.

-N VENDOR_DNS, --vendor-dns VENDOR_DNS
    Vendor DNS used to create vendor-id in manifest.

-s KEYFILE, --sign KEYFILE
    Sign manifest with the specified private key

-b, --bootloader
    Images contain a bootloader, application offset is determined by series

-c, --crc
    Append CRC32 to end of output file

-o OUTPUT, --output OUTPUT
    Output file path

Examples
--------

Create a plain upgrade for MDot from an image containing a bootloader and sign the manifest::

    multitool device plain -m -i MTDOT -s mykey.prv -b mdot_image_4.0.5.bin

Create a plain upgrade for XDot from an image containing a bootloader and sign the manifest::

    multitool device plain -i XDOT -s mykey.prv -b xdot_image_4.0.5.bin

manifest
========

Usage
-----

.. code-block::

    multitool device manifest [-h] [-a] [-f {text,hex}] [-d DESCRIPTION] [-I MODEL] [-v VERSION]
                              [-n VENDOR] [-N VENDOR_DNS] [-p ORIGVER] [-c] [-s KEYFILE] [-b]
                              [-o OUTPUT] series image

positional arguments
^^^^^^^^^^^^^^^^^^^^

image
    Path to firmware image

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    show this help message and exit

-a, --apply
    Add manifest to directly to image file

-f {text,hex}, --format {text,hex}
    Output format

-d DESCRIPTION, --description DESCRIPTION
    Description of upgrade

-i SERIES, --series SERIES
    Target hardware series

-I MODEL, --model MODEL
    A more precise hardware description than the series

-v VERSION, --version VERSION
    Firmware version in upgrade

-n VENDOR, --vendor VENDOR
    Vendor DNS used to create vendor-id in manifest.

-N VENDOR_DNS, --vendor-dns VENDOR_DNS
    Vendor DNS used to create vendor-id in manifest.

-p ORIGVER, --patch ORIGVER
    Image is a patch for original version ORIGVER

-c, --compressed
    Image is compressed

-s KEYFILE, --sign KEYFILE
    Sign manifest with the specified private key

-b, --bootloader
    Images contain a bootloader, application offset is determined by series

-o OUTPUT, --output OUTPUT
    Output file path

Examples
--------

.. code-block::

    multitool device manifest -i XDOT -s mykey.prv -b -o manifest.bin xdot_image_4.0.5.bin


verify
======

Usage
-----

.. code-block::

    multitool device verify [-h] image pub_key_file

positional arguments
^^^^^^^^^^^^^^^^^^^^

image
    Path to a image file

pub_key_file
    Path to public key file

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    show this help message and exit


crc
===

Usage
-----

.. code-block::

    multitool device crc [-h] [-o OUTPUT] image

positional arguments
^^^^^^^^^^^^^^^^^^^^

image
    Path to a image file

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    show this help message and exit

-o OUTPUT, --output OUTPUT
    Output file path


upgrade
=======

Usage
-----

.. code-block::

    multitool device upgrade [-h] [-b] [--command-interface] [-r BAUDRATE] [-x] series port image

positional arguments
^^^^^^^^^^^^^^^^^^^^
series
    Device series (MTDOT, XDOT, MTQ, MTQN)

port
    Serial port device name (COM3, /dev/ttyACM0, etc.)

image
    Path to firmware image

optional arguments
^^^^^^^^^^^^^^^^^^

-h, --help
    show this help message and exit

-b, --bootloader
    Images contain a bootloader

--command-interface
    Serial port is the device's AT command interface.

-r BAUDRATE, --baudrate BAUDRATE
    Serial port baudrate

-x, --no-processing
    Image already has CRC, use as-is

Examples
--------

.. code-block::

    multitool device upgrade -b XDOT COM4 xdot_image_4.0.4.bin
